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

Graph__builder.add_edge(START , "google_search")
Graph__builder.add_edge(START , "bing_search")
Graph__builder.add_edge(START , "reddit_search")

Graph__builder.add_edge("google_search" , "analyze_reddit_posts")
Graph__builder.add_edge("bing_search" , "analyze_reddit_posts")
Graph__builder.add_edge("reddit_search" , "analyze_reddit_posts")
Graph__builder.add_edge("analyze_reddit_posts" , "retrieve_reddit_post")
Graph__builder.add_edge("retrieve_reddit_post" , "analyze_google_results")
Graph__builder.add_edge("retrieve_reddit_post" , "analyze_bing_results")
Graph__builder.add_edge("retrieve_reddit_post" , "analyze_reddit_results")

Graph__builder.add_edge("analyze_google_results" , "synthesize_analysis")
Graph__builder.add_edge("analyze_bing_results" , "synthesize_analysis")
Graph__builder.add_edge("analyze_reddit_results" , "synthesize_analysis")

Graph__builder.add_edge("synthesize_analysis" , END)

graph = Graph__builder.compile()

def run_graph():
    print("langgraph-powered-autonomous-multi-source-research-agent")
    print("Type Exit to quit the program")
    While True:
        user_input = input("Enter your question: ")
        if user_input.lower() == "exit":
            print("Exiting the program.")
            break
        state ={
            "messages": [{"role":"user" , "content": user_input}],
            "user_question": user_input,
            "google_results": None,
            "bing_results": None,
            "reedit_results": None,
            "selected_reddit_urls": None,
            "reddit_post_data": None,
            "google_analysis": None,
            "bing_analysis": None,
            "reddit_analysis": None,
            "final_answer": None
        }

        print("\n Starting the research process...\n")
        print("Processing your question through the research graph...\n")
        final_state = graph.invoke(state)
        if finale_state.get("final_answer"):
            print("\nFinal Answer:\n")
            print(final_state["final_answer"])
        print("-" * 80)

if __name__ == "__main__":
    run_graph()
