from dotenv import load_dotenv
from typing import Annotated , List , Literal
from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from typing_extensions import TypedDict
from pydantic import BaseModel , Field
from web_operations import serp_search , reddit_search_api , reddit_post_retrieval
from langchain_core.documents import Document
from src.memory.memory_service import hybrid_search
from src.memory.vector_store import vector_store
from uuid import uuid4
from prompts import (get_reddit_url_analysis_messages

 , get_google_analysis_messages ,
  get_bing_analysis_messages ,
   get_reddit_analysis_messages ,
    get_synthesis_messages,
    )
from pydantic import BaseModel , Field

load_dotenv()

llm_for_classification = ChatOllama(model="llama3.2:3b")
llm_for_analysis = ChatOllama(model="llama3.2:3b")
class NeedStore(BaseModel):
    need_store: bool 
    memory : str | None
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
    memories : list | None
class reddit_url_analysis(BaseModel): #this will be called when we want to analyze the selected reddit urls so that our llm respect the structure of the data we want to get from the reddit urls
    selected_urls:List[str] = Field(... , description="List of selected Reddit URLs for further analysis")


def classification_of_user_question(state: State):
    user_question = state.get("user_question", "")

    print("Classifying user question:")

    structured_llm = llm_for_classification.with_structured_output(
        ResearchClassifier
    )

    prompt = f"""
You are an intelligent search-intent classifier for an AI research assistant.

Your task is to analyze the user's question and determine which search sources
are required to answer it accurately.

USER QUESTION:
{user_question}

AVAILABLE SEARCH SOURCES:
1. Google Search
2. Bing Search
3. Reddit Search

CLASSIFICATION RULES:

1. NO SEARCH REQUIRED:
   - Greetings, small talk, and casual conversations.
   - Questions about the user's personal information, preferences, or projects.
   - Follow-up questions answerable using conversation history or retrieved memories.
   - General questions that do not require recent or externally verified information.

2. GOOGLE + BING SEARCH:
   - Research requests about a specific topic.
   - Questions requiring external factual information.
   - Explanations, comparisons, or detailed research benefiting from multiple sources.
   - Questions about recent events, technologies, products, or developments.

3. REDDIT SEARCH:
   - Explicit requests for Reddit discussions, opinions, or experiences.
   - Questions about what Reddit users think about a topic.
   - Requests where community feedback is particularly relevant.

4. MULTIPLE SEARCH SOURCES:
   - General research + Reddit opinions: use all three sources.
   - Reddit-specific research: use Reddit only unless other sources are requested.
   - Select only sources that genuinely contribute to the answer.

5. UNCLEAR QUESTIONS:
   - Ambiguous but understandable research requests: use Google and Bing.
   - Questions too vague to understand: do not search; request clarification.

IMPORTANT:
- Prioritize the user's actual intent over individual keywords.
- Do not search for information already available in conversation history or memories.
- Prefer no search over unnecessary searches.
- Multiple sources can be selected simultaneously.

Return the classification using the required structured output schema.
Do not provide explanations outside the structured output.
CRITICAL DEFAULT RULE:

The default classification for any message is:
- need_google_search = false
- need_bing_search = false
- need_reddit_search = false

Only change a value to true when the user's message explicitly requires
external information or research.

A user describing their project, sharing personal information,
explaining what they are building, or having a normal conversation
NEVER requires a search.

Do not perform research simply because the message mentions
technologies, frameworks, tools, or websites.
INTENT VS DESCRIPTION:

You MUST distinguish between describing an activity and requesting
that activity.

Examples:

- "I'm building an agent that researches AI topics."
  -> NO SEARCH.

- "My goal is to retrieve information from Reddit."
  -> NO SEARCH.

- "I want my agent to use Google and Bing."
  -> NO SEARCH.

- "Research the latest developments in AI agents."
  -> GOOGLE + BING.

- "Find Reddit discussions about LangGraph."
  -> REDDIT ONLY.

A statement describing what the user is building, planning,
or wants to achieve is NOT a research request.

Only activate search when the user is actually asking you
to retrieve external information.
IMPORTANT: Questions about the user's own project, technologies,
architecture, previous decisions, or past conversations must NOT
trigger external searches.

Examples:
- "What technologies am I using in my AI research assistant?"
  -> Google: False, Bing: False, Reddit: False

- "What database did I choose for my project?"
  -> Google: False, Bing: False, Reddit: False

- "Find the latest technologies used in AI research agents."
  -> Google: True, Bing: True, Reddit: False
"""

    intent = structured_llm.invoke(prompt)
    print(intent.need_google_search , intent.need_bing_search , intent.need_reddit_search)
    return {
        "need_google_search": intent.need_google_search,
        "need_bing_search": intent.need_bing_search,
        "need_reddit_search": intent.need_reddit_search,
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
    structured_llm = llm_for_analysis.with_structured_output(reddit_url_analysis)
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
    reply = llm_for_analysis.invoke(messages)
    return {"google_analysis": reply.content}

def analyze_bing_results(state:State):
    print("Analyzing Bing search results...")
    user_question = state.get("user_question" , "")
    bing_results = state.get("bing_results" , "")
    messages = get_bing_analysis_messages(user_question , bing_results)
    reply = llm_for_analysis.invoke(messages)
    return {"bing_analysis": reply.content}

def analyze_reddit_results(state:State):
    print("Analyzing Reddit discussions...")
    user_question = state.get("user_question" , "")
    reddit_results = state.get("reddit_results" , "")
    reddit_post_data = state.get("reddit_post_data" , [])
    messages = get_reddit_analysis_messages(user_question , reddit_results , reddit_post_data)
    reply = llm_for_analysis.invoke(messages)
    return {"reddit_analysis": reply.content}

def synthesize_analysis(state:State):
    print("Synthesizing analysis from all sources...")
    user_question = state.get("user_question" , "")
    google_analysis = state.get("google_analysis" , "")
    bing_analysis = state.get("bing_analysis" , "")
    reddit_analysis = state.get("reddit_analysis" , "")
    messages = get_synthesis_messages(user_question , google_analysis , bing_analysis , reddit_analysis)
    reply = llm_for_analysis.invoke(messages)
    final_answer = reply.content
    return {"final_answer": final_answer , "messages":[{"role":"assistant" , "content": final_answer}]}
def general_response(state:State):
    user_question = state.get("user_question" , "")
    memories = state.get("memories" , [])
    memories_context = "\n".join(
        [memory.page_content for memory in memories]
    )
    prompt = f"""
    You are a helpful AI assistant.

    Relevant information from previous interactions:
    {memories_context}

    Use these memories when relevant to answer the user's question.
    Do not claim that you don't know information that is available
    in the provided memories.

    User question:
    {user_question}
    """
    llm_response = llm_for_analysis.invoke(prompt)
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

def retrieve_memories(state:State):
    user_question = state.get("user_question" , "")
    print(f"Retrieving memories related to the question: {user_question}")
    memories = hybrid_search(user_question)
    if memories:
        print(f"Retrieved {len(memories)} relevant memories.")
        return {"memories": memories}
    else:
        print("No relevant memories found.")
        return {"memories": []}

def store_memories(state: State):
    user_question = state.get("user_question", "")
    final_answer = state.get("final_answer", "")
    memory_id = str(uuid4())
    if user_question and final_answer:
        answer = llm_for_classification.with_structured_output(
            NeedStore
        ).invoke(
            f"""
            Based on the user question:
            {user_question}

            And the final answer:
            {final_answer}

            Should this interaction be stored as a useful
            memory for future reference?
            if yes please provide a brief summary of the memory to be stored in the memory field if not then  put None 
            """
        )

        if answer.need_store and answer.memory:

            memory_entry = Document(
                page_content=answer.memory,
                metadata={
                    "type": "research_memory",
                    "id": memory_id
    }
)

            vector_store.add_documents([memory_entry],
            ids=[memory_id]
            )

            print("Memory stored successfully.")

        else:
            print("No useful memory to store.")

    return {}
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
Graph__builder.add_node("retrieve_memories", retrieve_memories)
Graph__builder.add_node("store_memories", store_memories)
Graph__builder.add_node("analyze_reddit_results" , analyze_reddit_results)
Graph__builder.add_node("synthesize_analysis" , synthesize_analysis)
Graph__builder.add_node("classification_of_user_question" , classification_of_user_question)
Graph__builder.add_edge(START, "retrieve_memories")
Graph__builder.add_edge("retrieve_memories", "classification_of_user_question")

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

Graph__builder.add_edge(
    "synthesize_analysis",
    "store_memories"
)

Graph__builder.add_edge(
    "general_response",
    "store_memories"
)

Graph__builder.add_edge("store_memories", END)

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
