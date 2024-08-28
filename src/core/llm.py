from __future__ import annotations
from flask import Flask, current_app as app, g
from typing import Dict, Any
import threading

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import (
    create_retrieval_chain,
    create_history_aware_retriever,
)

# from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_pinecone import PineconeVectorStore

# from langchain.globals import set_debug


class LangChain:
    def __init__(self):
        api_key = app.config["OPENAI_API_KEY"]
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo-0125")
        self.embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-small",
            dimensions=512,
        )
        self.store = {}
        self.timer_duration = 5 * 60  # 5 minutes
        self.max_messages = 5
        # set_debug(True)

    def init_vector_db(self) -> None:
        # already added collection to db
        self.db = PineconeVectorStore(
            index_name=app.config["PINECONE_INDEX_NAME"],
            embedding=self.embeddings,
        )

    def plan(self, input: Dict[str, Any]):
        template = """Given the following <context>{context}</context>.
        Suggest places to visit based on the following information: {input}.
        - The higher the review and rankings, the better the location. Prioritise locations with higher rankings and reviews.
        - The results need not be exact matches to the user's preferred activities, you can suggest other locations not relevant to the activities.
        But if possible, prioritise the locations that are relevant to the user's preferred activities.
        In case the number of places doesn't meet the minimum requirement, suggest more locations based on their similarity to the user's city.
        - The returned format should be a list of items in JSON format with the same fields as in the database, parent field is "locations".
        - The results should be different from the previous results, but doesn't necessarily have to be completely different.
        - Strip any newline characters from the result.
        """

        retriever = self.db.as_retriever(
            search_kwargs={"k": 5, "filter": {"city": input["city"]}},
            # search_type="mmr",
            # search_kwargs={
            #     "k": 5,
            #     "filter": {"city": input["city"]},
            #     "lambda_mult": 0.2,
            #     "fetch_k": 20,
            # },
        )

        prompt = ChatPromptTemplate.from_template(template)
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, prompt
        )
        rag_chain = create_retrieval_chain(retriever, history_aware_retriever)
        chain_with_history = RunnableWithMessageHistory(
            rag_chain,
            get_session_history=self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=int,
                    name="User ID",
                    description="Unique identifier for the user",
                    default=0,
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="city",
                    annotation=str,
                    name="City",
                    description="Unique name of the city",
                    default="",
                    is_shared=True,
                ),
            ],
        )
        config = {
            "configurable": {
                "user_id": input["user_id"],
                "city": input["city"],
            },
        }
        chain_with_trimming = (
            RunnablePassthrough.assign(
                messages_trimmed=self.trim_messages(input["user_id"], input["city"])
            )
            | chain_with_history
        )
        res = chain_with_trimming.invoke(
            input={
                "input": "City: "
                + input["city"]
                + "\nPreferences: "
                + input["preferences"],
            },
            config=config,
        )

        res = self.parse_output(res["answer"])
        # self.add_images_mock(res)
        self.add_images(res, input["city"])
        return res

    def parse_output(self, docs) -> Dict[str, Any]:
        res = []
        for doc in docs:
            items = doc.page_content.split("\n")
            data = {}
            for item in items:
                entry = item.split(":")
                key = entry[0].strip()

                if key == "opening_hours" or key == "website":
                    value = ":".join(entry[1:]).strip()
                else:
                    value = (entry[1] or "").strip()

                if key == "rankings" or key == "reviews":
                    value = float(value) if value else 0
                if key == "id":
                    value = int(value)
                if key == "lat" or key == "lng":
                    value = float(value) if value else 0
                data[key] = value

            res.append(data)

        return {"locations": res}

    def get_session_history(self, user_id: int, city: str) -> BaseChatMessageHistory:
        if (user_id, city) not in self.store:
            self.store[(user_id, city)] = ChatMessageHistory()
            # create a timer to clear the store
            timer = threading.Timer(
                self.timer_duration, self.clear_key, args=(user_id, city)
            )
            timer.start()
        return self.store[(user_id, city)]

    def clear_key(self, user_id: int, city: str) -> None:
        if (user_id, city) in self.store:
            del self.store[(user_id, city)]

    def trim_messages(self, user_id: int, city: str) -> callable:
        def trim(chain_input) -> bool:
            current_session = self.get_session_history(user_id, city)
            stored_messages = current_session.messages
            if len(stored_messages) <= self.max_messages:
                return False
            current_session.clear()
            for message in stored_messages[-self.max_messages :]:
                current_session.add_message(message)
            return True

        return trim

    def add_images(self, res, city) -> None:
        search = GoogleSerperAPIWrapper(type="images", gl="vn")
        images = {}

        for item in res["locations"]:
            name = item["name"]
            if name not in images:
                data = search.results(name + " " + city)
                image_items = data["images"][:10]  # get 10 images
                images[name] = [image["imageUrl"] for image in image_items]
            item["images"] = images[name]

    def add_images_mock(self, res) -> None:
        for item in res["locations"]:
            item["images"] = [app.config["MOCK_IMAGE_LINK"] for _ in range(5)]

    @classmethod
    def get_instance(cls) -> LangChain:
        llm = getattr(g, "_llm", None)
        if llm is None:
            llm = g._llm = cls()
        return llm

    @staticmethod
    def init_app(app: Flask) -> None:
        llm = LangChain.get_instance()
        app.config["LLM"] = llm
