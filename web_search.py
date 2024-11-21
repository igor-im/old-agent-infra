from tavily import TavilyClient

api_token = os.environ.get('TAVILY_API_TOKEN')

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key=api_token)


def search(query):
    response = tavily_client.search(query)
    return response


def get_context(query):
    response = tavily_client.get_search_context(query)
    return response


def get_answer(query):
    response = tavily_client.qna_search(query)
    return response
