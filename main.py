import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from langchain_core.runnables.utils import Input, Output
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
from psycopg import Connection, AsyncConnection

from conversation_tools import State, summarize_conversation, should_continue
from llm import run_llm, tools
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langserve import add_routes

load_dotenv()

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

DB_URI = os.environ.get("CONVERSATIONS_POSTGRES_URL")
connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}


@asynccontextmanager
async def lifespan(l_app: FastAPI) -> AsyncGenerator[None, None]:
    # Construct agent with Sqlite checkpointer
    async with await AsyncConnection.connect(DB_URI, **connection_kwargs) as l_conn:
        workflow.checkpointer = l_conn
        l_app.state.agent = workflow
        yield
    # context manager will clean up the AsyncSqliteSaver on exit


app = FastAPI(lifespan=lifespan)

# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", run_llm)
workflow.add_node("run_llm", run_llm)
workflow.add_node(summarize_conversation)
workflow.add_node("tools", ToolNode(tools))

# Set the entrypoint as conversation
workflow.add_edge(START, "run_llm")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_conditional_edges(
    "run_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
workflow.add_edge("summarize_conversation", END)

# # memory = init_checkpointer()
# with Connection.connect(DB_URI) as conn:
#     checkpointer = PostgresSaver(conn)
#     react_graph_memory = workflow.compile(checkpointer=checkpointer)

# Specify a thread
config = {"configurable": {"thread_id": "2"}}


#
# # Start conversation
# input_message = HumanMessage(content="hi! I'm Lance")
# output = react_graph_memory.invoke({"messages": [input_message]}, config)
# for m in output['messages'][-1:]:
#     m.pretty_print()
#
# input_message = HumanMessage(content="what's my name?")
# output = react_graph_memory.invoke({"messages": [input_message]}, config)
# for m in output['messages'][-1:]:
#     m.pretty_print()
#
# input_message = HumanMessage(content="i like the 49ers!")
# output = react_graph_memory.invoke({"messages": [input_message]}, config)
# for m in output['messages'][-1:]:
#     m.pretty_print()


def process_message(message):
    # memory = init_checkpointer()
    with Connection.connect(DB_URI) as conn:
        print("process_message: " + message.content)
        checkpointer = PostgresSaver(conn)
        react_graph_memory = workflow.compile(checkpointer=checkpointer)
        input_message = message
        output = react_graph_memory.invoke({"messages": [input_message]}, config)
        for m in output['messages'][-1:]:
            m.pretty_print()
        return output


# process_message(HumanMessage(content="hi! I'm Lance"))
# process_message(HumanMessage(content="what's my name?"))
# process_message(HumanMessage(content="i like the 49ers! do you?"))
# process_message(HumanMessage(content="what is 2-5?"))
# process_message(HumanMessage(content="add 3 to that?"))
# process_message(HumanMessage(content="what's my name?"))


@app.get("/")
async def root_route():
    return "Hello World"


# @app.get("/chat/{thread_id}")
# async def chat_thread():
#     return "Hello World"
#
#

@app.get("/chat/threads")
async def chat_thread():
    with Connection.connect(DB_URI) as conn:
        checkpointer = PostgresSaver(conn)
        threads = checkpointer.list({})
        response = []
        for thread in threads:
            response.append(thread)
        return response


with Connection.connect(DB_URI) as conn:
    tcheckpointer = PostgresSaver(conn)
    react_graph_memory = workflow.compile(checkpointer=tcheckpointer)

add_routes(
    app,
    react_graph_memory.with_types(input_type=Input, output_type=Output),
    path="/chat",
)

#
#
# @app.post("/chat/{thread_id}")
# async def chat_thread():
#     return "Hello World"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8500)
