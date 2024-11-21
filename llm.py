import os

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from conversation_tools import State

base_path = "http://localhost:10550/v1"
model_name = os.environ.get('MODEL_NAME', 'gpt-4')
os.environ['OPENAI_API_KEY'] = 'sk-OPENAI_API_KEY'


def math_evaluator(expression):
    """evaluates a math expression
    Args:
            expression: math expression
    """
    print("Math eval processing: " + expression)
    return eval(expression)


tools = [math_evaluator]


def run_llm(state: State):
    # Get summary if it exists
    summary = state.get("summary", "")

    # If there is summary, then we add it
    if summary:

        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"

        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]

    base_llm = ChatOpenAI(openai_api_base=base_path, model="gpt-4", temperature=0.0)
    llm = base_llm.bind_tools(tools)
    print("Running llm: " + str(messages))
    response = llm.invoke(messages)
    return {"messages": response}
