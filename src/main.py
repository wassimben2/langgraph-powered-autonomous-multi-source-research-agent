from dotenv import load_dotenv
from typing import Annotated , List , Literal
from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from typing_extensions import TypedDict
from pydantic import BaseModel , Field
from web_operations import serp_search , reddit_search_api , reddit_post_retrieval
from prompts import (get_reddit_url_analysis_messages
 , get_google_analysis_messages ,
  get_bing_analysis_messages ,
   get_reddit_analysis_messages ,
    get_synthesis_messages,
    )
from pydantic import BaseModel , Field

load_dotenv()

llm = ChatOllama(model="qwen2.5:0.5b" )
class ResearchClassifier(BaseModel):
    need_google_search: bool 
    need_bing_search: bool 
    need_reddit_search: bool 
class State(TypedDict):
    messages:Annotated[list , add_messages] ##this a list of messages that will call the add_messages function to add messages to the state
    user_question :str | None
    google_results :str | None
    bing_results : str | None
    reddit_results : str | None
    selected_reddit_urls : List[str] | None
    reddit_post_data : list | None
    google_analysis : str | None
    bing_analysis : str | None
    reddit_analysis : str | None
    final_answer : str | None
    need_google_search : bool | None
    need_bing_search : bool | None
    need_reddit_search : bool | None
class reddit_url_analysis(BaseModel): #this will be called when we want to analyze the selected reddit urls so that our llm respect the structure of the data we want to get from the reddit urls
    selected_urls:List[str] = Field(... , description="List of selected Reddit URLs for further analysis")

def classification_of_user_question(state:State):
    user_question = state.get("user_question", "")
    print(f"Classifying user question:")
    strucutred_llm = llm.with_structured_output(ResearchClassifier)
    prompt = f"based on the user question : {user_question} , classify the question into one of the following categories : 1. need_google_search 2. need_bing_search 3. need_reddit_search 4. none of the above . If the question requires multiple searches, please indicate that as well , to determine which searches are needed , you can just ask yourself is the user greeting me if yes then no search is needed , is the user asking me to do a research on a specific topic if yes then we need to do a search on google and bing , is the user asking me to find information from reddit if yes then we need to do a search on reddit , if the question is not clear enough to determine which searches are needed , please indicate that as well ."
    intent = strucutred_llm.invoke(prompt)
    return {
            "need_google_search": intent.need_google_search ,
            "need_bing_search": intent.need_bing_search ,
            "need_reddit_search": intent.need_reddit_search
    }

def google_search(state:State):
    user_question = state.get("user_question" , "")
    print(f"Performing Google search for: {user_question}")
    google_results=serp_search(user_question , engine="google")
    print("Google search completed.")
    
    return {"google_results": google_results}

def bing_search(state:State):
    user_question = state.get("user_question" , "")
    print(f"Performing Bing search for: {user_question}")
    bing_results=serp_search(user_question , engine="bing")
    print("Bing search completed.")
   

    return {"bing_results": bing_results}

def reddit_search(state:State):
    user_question = state.get("user_question" , "")
    print(f"Performing Reddit search for: {user_question}")
    reddit_results=reddit_search_api(user_question)
    
    return {"reddit_results": reddit_results}

def analyze_reddit_posts(state:State):
    user_question = state.get("user_question" , "")
    reddit_results = state.get("reddit_results" , "")
    if not reddit_results:
        return {"selected_reddit_urls": []}
    structured_llm = llm.with_structured_output(reddit_url_analysis)
    messages = get_reddit_url_analysis_messages(user_question , reddit_results)
    try:
        analysis = structured_llm.invoke(messages)
        selected_urls = analysis.selected_urls
        for i ,url in enumerate(selected_urls ,1):
            print(f"Selected URL {i}: {url}")
        return {"selected_reddit_urls": selected_urls}
    except Exception as e:
        print(f"Error analyzing Reddit posts: {e}")
        selected_urls = []
    return {"selected_reddit_urls": []}

def retrieve_reddit_post(state:State):
    print("Retrieving Reddit post data...")
    selected_urls = state.get("selected_reddit_urls" , [])
    if not selected_urls:
        print("No selected Reddit URLs to retrieve.")
        return {"reddit_post_data": []}
    print(f"Processing {len(selected_urls)} selected Reddit URLs...")
    reddit_post_data = reddit_post_retrieval(selected_urls)
    if reddit_post_data:
        print(f"Successfully retrieved data for {len(reddit_post_data)} Reddit posts.")
        return {"reddit_post_data": reddit_post_data}
    else:
        print("Failed to retrieve Reddit post data.")
        return {"reddit_post_data": []}
    return {"reddit_post_data":reddit_post_data}

def analyze_google_results(state:State):
    print("Analyzing Google search results...")
    user_question = state.get("user_question" , "")
    google_results = state.get("google_results" , "")
    messages = get_google_analysis_messages(user_question , google_results)
    reply = llm.invoke(messages)
    return {"google_analysis": reply.content}

def analyze_bing_results(state:State):
    print("Analyzing Bing search results...")
    user_question = state.get("user_question" , "")
    bing_results = state.get("bing_results" , "")
    messages = get_bing_analysis_messages(user_question , bing_results)
    reply = llm.invoke(messages)
    return {"bing_analysis": reply.content}

def analyze_reddit_results(state:State):
    print("Analyzing Reddit discussions...")
    user_question = state.get("user_question" , "")
    reddit_results = state.get("reddit_results" , "")
    reddit_post_data = state.get("reddit_post_data" , [])
    messages = get_reddit_analysis_messages(user_question , reddit_results , reddit_post_data)
    reply = llm.invoke(messages)
    return {"reddit_analysis": reply.content}

def synthesize_analysis(state:State):
    print("Synthesizing analysis from all sources...")
    user_question = state.get("user_question" , "")
    google_analysis = state.get("google_analysis" , "")
    bing_analysis = state.get("bing_analysis" , "")
    reddit_analysis = state.get("reddit_analysis" , "")
    messages = get_synthesis_messages(user_question , google_analysis , bing_analysis , reddit_analysis)
    reply = llm.invoke(messages)
    final_answer = reply.content
    return {"final_answer": final_answer , "messages":[{"role":"assistant" , "content": final_answer}]}
def general_response(state:State):
    user_question = state.get("user_question" , "")
    print(f"User question: {user_question}")
    llm_response = llm.invoke(user_question)
    return {"final_answer": llm_response.content , "messages":[{"role":"assistant" , "content": llm_response.content}]}

def route_search(state:State):
    
    need_google_search = state.get("need_google_search" , False)
    need_bing_search = state.get("need_bing_search" , False)
    need_reddit_search = state.get("need_reddit_search" , False)
    
    if need_google_search and need_bing_search and need_reddit_search:
        print("All searches are needed. Proceeding to search on Google, Bing, and Reddit.")
        return ["google_search" , "bing_search" , "reddit_search"]
    elif need_google_search and need_bing_search:
        print("Google and Bing searches are needed. Proceeding to search on Google and Bing.")
        return ["google_search" , "bing_search"]
    elif need_google_search and need_reddit_search:
        print("Google and Reddit searches are needed. Proceeding to search on Google and Reddit.")
        return ["google_search" , "reddit_search"]
    elif need_bing_search and need_reddit_search:
        print("Bing and Reddit searches are needed. Proceeding to search on Bing and Reddit.")
        return ["bing_search" , "reddit_search"]
    elif need_google_search:
        print("Only Google search is needed. Proceeding to search on Google.")
        return "google_search"
    elif need_bing_search:
        print("Only Bing search is needed. Proceeding to search on Bing.")
        return "bing_search"
    elif need_reddit_search:
        print("Only Reddit search is needed. Proceeding to search on Reddit.")
        return "reddit_search"
    else:
        print("No search needed. Proceeding to general response.")
        return "general_response"

Graph__builder = StateGraph(State)
Graph__builder.add_node("google_search" , google_search)
Graph__builder.add_node("bing_search" , bing_search)
Graph__builder.add_node("reddit_search" , reddit_search)
Graph__builder.add_node("analyze_reddit_posts" , analyze_reddit_posts)
Graph__builder.add_node("retrieve_reddit_post" , retrieve_reddit_post)
Graph__builder.add_node("general_response" , general_response)
Graph__builder.add_node("route_search" , route_search)
Graph__builder.add_node("analyze_google_results" , analyze_google_results)
Graph__builder.add_node("analyze_bing_results" , analyze_bing_results)
Graph__builder.add_node("analyze_reddit_results" , analyze_reddit_results)
Graph__builder.add_node("synthesize_analysis" , synthesize_analysis)
Graph__builder.add_node("classification_of_user_question" , classification_of_user_question)
Graph__builder.add_edge(START , "classification_of_user_question")

Graph__builder.add_conditional_edges(
    "classification_of_user_question" ,
     route_search,
    {
        "google_search": "google_search",
        "bing_search": "bing_search",
        "reddit_search": "reddit_search",
        "general_response": "general_response",
    }
)
Graph__builder.add_edge("route_search" , "general_response")
Graph__builder.add_edge("route_search" , "google_search")
Graph__builder.add_edge("route_search" , "bing_search")
Graph__builder.add_edge("route_search" , "reddit_search")

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
    program_start = True
    while program_start:
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
        if final_state.get("final_answer"):
            print("\nFinal Answer:\n")
            print(final_state["final_answer"])
        print("-" * 80)

if __name__ == "__main__":
    run_graph()
