from dotenv import load_dotenv
import os , requests

from urllib.parse import quote_plus
from snapshot import poll_snapshot_status , download_snapshot
load_dotenv()
dataset_posts = os.getenv("DATASET_POSTS")
dataset_comments = os.getenv("DATASET_COMMENTS")
print(f"Dataset for posts: {dataset_posts}")
print(f"Dataset for comments: {dataset_comments}")
def _make_API_request(url , **kwargs): ##making a request to bright data API to get the data from the url
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    if not api_key:
        raise ValueError("BRIGHTDATA_API_KEY is not set in the environment variables.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url , headers=headers , **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def serp_search(query:str , engine):
   if engine == "google": ##those are the engine we will use to make our research
        base_url = "https://google.com/search"
   elif engine == "bing":
        base_url = "https://bing.com/search"
   else:
        raise ValueError(f"Unsupported search engine: {engine}. Supported engines are 'google' and 'bing'.")
   url = "https://api.brightdata.com/request" ## this the url we'll be using to make our request to the bright data API
   payload ={
        "zone":"ai_agent",
        "url": f"{base_url}?q={quote_plus(query)}", ##this the url we'll be using that contains the base url and the question we want to search for and we used quote_plus to encode the question to make it url safe   
        "format":"raw"
    }
   final_response = _make_API_request(url , json=payload)
   if not final_response:
       print("No response received from the API.")
       return None
   extracted_data ={
       "knowledge": final_response.get("knowledge" , {}),
       "organic": final_response.get("organic" , [])
    }
   return extracted_data
    # ## i used to get the knowledge and organic data from the response because this an example of what data is contained inside those keys
    # ##let's try a research from the bright data API and as a query (question ) i'll put minecraft and the engine i'll use will be google
    # ##"knowledge": {
    # "name": "Minecraft",
    # "summary": "Video game",
    # "subtitle": "Video game",
    # "description": "Minecraft is a sandbox video game developed and published by the Swedish company Mojang Studios. Following its initial public alpha release as an early access title on 17 May 2009, it was formally released on 18 November 2011 for personal computers.",
    # "description_source": "Wikipedia",
    # "description_link": "https://www.google.com/goto?url=CAESZAHEIkXXMA7Zxvzscn-8eKc4kwskspaDUV8OASE61FAzL_sd22s3r_BtU9CxGc5iiKMOebM6hUuGKDeRsKEnutnkeUDajoIXeOAGW_ytHTea1F-htkspd7QW7u4VSDBKs8QjseE",
    # "images": [
    #   {
    #     "image": "data:image/webp;base64,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",
    #     "image_alt": "Image of Review: Surviving the pandemic with 'Minecraft' | HS Insider",
    #     "image_base64": "data:image/webp;base64,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"
    #   },
    #   {
    #     "image": "data:image/webp;base64,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",
    #     "image_alt": "Image of The history of Minecraft",
    #     "image_base64": "data:image/webp;base64,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"
    #   },
    # ..........
    ## and for the organic
    ##"organic": [
    # {
    #   "link": "https://www.minecraft.net/en-us",
    #   "source": "Minecraft",
    #   "display_link": "https://www.minecraft.net › en-us",
    #   "title": "Welcome to the Minecraft Official Site | Minecraft",
    #   "description": "Explore new gaming adventures, accessories, & merchandise on the Minecraft Official Site. Buy & download the game here, or check the site for the latest ...",
    #   "snippet_highlighted_words": [
    #     "Minecraft"
    #   ],
    #   "extensions": [
    #     {
    #       "type": "site_link",
    #       "extended": true,
    #       "text": "Download the Launcher",
    #       "link": "https://www.google.com/goto?url=CAESZQHEIkXX6h8cMHAAtqSdbEKaHx6x5mROOsr5qIvmAEVNRZWnBGa4HN66o9NU7aHwn8wFKUbGI1MopG1cN0xlDLPgsMWSJxbunmt7v67MreiTn2WFqeYJxQ0eNVtEdkmqzq8y8Y-J",
    #       "description": "Download Minecraft for Windows, Mac, and more. Download ...",
    #       "rank": 1
    #     },
    #     {
    #       "type": "site_link",
    #       "extended": true,
    #       "text": "Minecraft Education",
    #       "link": "https://www.google.com/goto?url=CAESYgHEIkXXJsCy65BWqBKurrVx1D9MPt-_k-yPcCDdKUO_7sf4UCZVHnd89LtapXpQ9QKrF2hw0PT37ZebShauiMhpb0Xm_pD0TwYFKDbFPuDw2j8tQ1Oq1JYIYMa9TRkySfVO",
    #       "description": "Get Minecraft Education for your classroom. Find out how using ...",
    #       "rank": 2
    #     },
    #     {
    #       "type": "site_link",
    #       "extended": true,
    #       "text": "Sign In or Sign Up",
    #       "link": "https://www.google.com/goto?url=CAESYgHEIkXXZLahQz11MXvRqzcRDYDg165WSncqIOLLhPMjWn29NoO-OO9-SjumFwF2DFxMDur-1PdeearHZ6J7aCA6lWRqDa7m_qjqvQHthBnNXs1CvfNsBI5vmaIDpTQ0bvf9",
    #       "description": "Sign in or sign up to conveniently manage your games and wallet ...",
    #       "rank": 3
    #     },
    #     {
    #       "type": "site_link",
    #       "extended": true,
    #       "text": "Games",
    #       "link": "https://www.google.com/goto?url=CAESbAHEIkXX94rGlzU8dmsOaYxvFSuVRMgmsowfvO1Ri_3T9IpCR52XtuC5W6bhK_S7jMlC53VsCsg_B8OlkcU-N0WEchfsgEQaSmFzZMg6mgiGJ_n2f2en8Fr0AvsxHy63PbjdgrabYJSb_mPQQA",
    #       "description": "Learn more about Minecraft, an action-adventure sandbox ...",
    #       "rank": 4
    #     },
    #     ......
    #so as u can see the organic and knowledge results contain some pretty useful information that we can use to display
def _trigger_and_download_snapshot(trigger_url, params, data ):
    trigger_result = _make_API_request(trigger_url, params=params, json=data)
    if not trigger_result:
        return None
    snapshot_id = trigger_result.get("snapshot_id")
    if not snapshot_id:
        return None
    if not poll_snapshot_status(snapshot_id):
        return None
    raw_data = download_snapshot(snapshot_id)
    return raw_data
def reddit_search_api(keyword , date="All time" , sort_by="Hot" , num_of_posts=75):
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
    params={
        "dataset_id": dataset_posts,
        "include_errors": "true",
        "type":"discover_new",
        "discover_by":"keyword"
    }
    data =[{
        "keyword" :keyword,
        "date" : date,
        "sort_by" : sort_by,
        "num_of_posts" : num_of_posts
    }]
    raw_data = _trigger_and_download_snapshot(trigger_url, params, data )
    if not raw_data:
        return None
    parsed_data = []
    for post in raw_data:
        pared_post ={
            "title": post.get("title"),
            "url": post.get("url"),
            
        }
        parsed_data.append(pared_post)
    return {"parsed_posts": parsed_data, "total_found": len(parsed_data)}
    return None

def reddit_post_retrieval(urls , days_back=10 , load_all_replies = False , comment_limit=""):
    if not urls:
        return None
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
    params={
        "dataset_id":dataset_comments,
        "include_errors": "true",
        
    }
    data=[{
        "urls": url,
        "days_back": days_back,
        "load_all_replies": load_all_replies,
        "comment_limit": comment_limit
    }
    for url in urls
    ]
    raw_data = _trigger_and_download_snapshot(trigger_url, params, data )
    if not raw_data:
        return None
    parsed_comments = []
    for comment in raw_data:
        pared_comment ={
            "comment_id": comment.get("comment_id"),
            "content": comment.get("comment"),
            "date": comment.get("date_posted"),
            
            
        }
        parsed_comments.append(pared_comment)
        return {"comments": parsed_comments, "total_found": len(parsed_comments)}













## so here basically what i made is use to scrapers from brighdata where one scrapes for reddits url and the other one scrapes for the posts and comments of those urls that i fetched 