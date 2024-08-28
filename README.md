# Tabi-AI

A service that provides APIs for planning trips and integrating a small recommendation system, used with other backends in our final year project Tabi. This project is for educational purposes only and is not intended for commercial use.

The project uses some Cloud services, you have to provide the keys to them like in the `.env.example` file in order to use. Or you can just view this repo as a simple example for developing.

_Updated:_ I removed the `data.csv` for now due to privacy concerns.

## Technology

- Flask
- Pinecone
- LangChain
- ChatGPT

## Prerequisites

- Python >= 3.7
- pip
- Docker (optional)
- Docker Compose (optional)

## Quick Start

### Initialize the Python env

Copy all the values in `.env.example` to your `.env` file.

If you are developing for the first time and don't have the `env` directory, run the following to initialize it and install the dependencies:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

You should only run this command once when first clone the repo to create the `env` directory. All of the dependencies are installed in the virtual environment and not on your system so don't worry.

### Develop

Before developing, make sure to source the `env`:

```bash
source env/bin/activate
```

You will see the environment name in your terminal. Now, you can develop as usual:

### Initialize the vector DB Collection

**Only for admin**

Run `python3 init.py` to persist the data collections to Pinecone Cloud. This will take a while. This process will only need to be done once. When you have the collections already, you can skip this step.

### Run the whole system

Make sure you have the collection persited. Then, you can run the whole system:

- As developing mode: `make run`. This will start the server in development mode. The server will be running on `localhost:5000`.
- As a Docker container: `docker compose up`. This will start the server. Used to integrate with other services, like Front-end application. The server will be running on `localhost:5001`.
