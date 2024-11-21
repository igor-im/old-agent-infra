import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore

load_dotenv()

weaviate_cluster_url = os.environ.get('WEAVIATE_URL')
weaviate_api_key = os.environ.get('WEAVIATE_API_KEY')

base_path = os.environ.get('OPENAI_API_BASE')

embeddings = OpenAIEmbeddings(openai_api_base=base_path, model="text-embedding-ada-002")

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_cluster_url,
    auth_credentials=weaviate.AuthApiKey(api_key=weaviate_api_key),
)
db = WeaviateVectorStore(weaviate_client, "LangChain_47d13db5141e4e3fbffa38155fc86df8", "text", embeddings)


def load_text_file(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    db.from_documents(docs, embeddings)
    weaviate_client.close()


def query_knowledge_base(query):
    res_docs = db.similarity_search(query)
    weaviate_client.close()
    return res_docs


print(query_knowledge_base("What is the capital of France?"))
