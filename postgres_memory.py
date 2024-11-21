from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from dotenv import load_dotenv
import os

load_dotenv()

DB_URI = os.environ.get("CONVERSATIONS_POSTGRES_URL")

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}


# def init_checkpointer():
#     with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
#         return checkpointer
