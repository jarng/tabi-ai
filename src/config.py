import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
    MOCK_IMAGE_LINK = os.environ.get("MOCK_IMAGE_LINK")
    TABI_BOOKING_BASE_URL = os.environ.get("TABI_BOOKING_BASE_URL")
    CHROMA_DB_PORT = os.environ.get("CHROMA_DB_PORT")
    CHROMA_DB_HOST = os.environ.get("CHROMA_DB_HOST")
    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
    # GEOCODING_API_KEY = os.environ.get("GEOCODING_API_KEY")

    @staticmethod
    def init_app(app):
        app.config["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        app.config["SERPER_API_KEY"] = Config.SERPER_API_KEY
        app.config["MOCK_IMAGE_LINK"] = Config.MOCK_IMAGE_LINK
        app.config["TABI_BOOKING_BASE_URL"] = Config.TABI_BOOKING_BASE_URL
        app.config["CHROMA_DB_PORT"] = Config.CHROMA_DB_PORT
        app.config["CHROMA_DB_HOST"] = Config.CHROMA_DB_HOST
        app.config["PINECONE_API_KEY"] = Config.PINECONE_API_KEY
        app.config["PINECONE_INDEX_NAME"] = Config.PINECONE_INDEX_NAME
        # app.config["GEOCODING_API_KEY"] = Config.GEOCODING_API_KEY
        app.app_context().push()


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    ENV = "development"
    FLASK_ENV = "development"
    FLASK_DEBUG = 1

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    "dev": DevelopmentConfig,
    "default": DevelopmentConfig,
}
