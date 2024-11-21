from langchain_core.prompts import PromptTemplate

from llm import run_llm

prompt_tpl = PromptTemplate.from_template(
    """Utilizing the agent list, determine which agent the user's question should be routed to, if you have a tool to solve the question use the tool instead. Answer with 
    the name of the agent only: 
     agent list: 
     {agent_list}
     
     user question: 
     {question}
    """
)


def route_question(question, agent_list):
    prompt = prompt_tpl.format(question=question, agent_list=agent_list)
    response = run_llm(prompt)
    return response
