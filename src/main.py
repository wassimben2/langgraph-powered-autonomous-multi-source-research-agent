from dotenv import load_dotenv
from typing import Annotated , List
from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import Message
from langchain.chat_models import init_chat_model
from typing_extensions import TypeDict
from pydantic import BaseModel , Field

load_dotenv()

llm = init_chat_model("qwen2.5:0.5b")

class State(TypeDict):
    messages:Annotated[list , add_messages] ##this a list of messages that will call the add_messages function to add messages to the state
    user_question :str | None
    google_results :str | None
    bing_results : str | None
    reedit_results : str | None
    selected_reddit_urls : List[str] | None
    reddit_post_data : list | None
    google_analysis : str | None
    bing_analysis : str | None
    reddit_analysis : str | None
    final_answer : str | None

def google_search(state:State)
    return

def bing_search(state:State)
    return

def reddit_search(state:State)
    return

def analyze_reddit_posts(state:State)
    return

def retrieve_reddit_post(state:State)
    return

def analyze_google_results(state:State)
    return

def analyze_bing_results(state:State)
    return

def analyze_reddit_results(state:State)
    return

def synthesize_analysis(state:State)
    return

Graph__builder = StateGraph(State)
Graph__builder.add_node("google_search" , google_search)
Graph__builder.add_node("bing_search" , bing_search)
Graph__builder.add_node("reddit_search" , reddit_search)
Graph__builder.add_node("analyze_reddit_posts" , analyze_reddit_posts)
Graph__builder.add_node("retrieve_reddit_post" , retrieve_reddit_post)
Graph__builder.add_node("analyze_google_results" , analyze_google_results)
Graph__builder.add_node("analyze_bing_results" , analyze_bing_results)
Graph__builder.add_node("analyze_reddit_results" , analyze_reddit_results)
Graph__builder.add_node("synthesize_analysis" , synthesize_analysis)