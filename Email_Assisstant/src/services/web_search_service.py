import os  
import httpx  # Asynchronous HTTP client for making requests  

# Google Custom Search API endpoint  
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"  

# Fetch the Google API key and search engine ID from environment variables  
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')  

async def web_search(query: str):  
    """  
    Perform a web search using the Google Custom Search API.  

    :param query: The search query string.  
    :return: A list of formatted search results or an empty list if none found.  
    """  
    params = {  
        'key': GOOGLE_API_KEY,  # Your Google API key  
        'cx': SEARCH_ENGINE_ID,  # Your Custom Search Engine ID  
        'q': query,              # The search query  
    }  

    async with httpx.AsyncClient() as client:  
        response = await client.get(GOOGLE_SEARCH_URL, params=params)  
        response.raise_for_status()  # Raise an error for any HTTP errors  
        search_results = response.json()  # Parse the JSON response  

    # Extracting relevant data from search results  
    formatted_results = []  
    for item in search_results.get('items', []):  
        formatted_result = {  
            'title': item.get('title'),  
            'link': item.get('link'),  
            'snippet': item.get('snippet'),  
        }  
        formatted_results.append(formatted_result)  

    return formatted_results  

# Optional function to determine the relevance of the results  
def filter_relevant_results(results, keyword):  
    """  
    Filter results based on keyword relevance.  

    :param results: List of search results.  
    :param keyword: Keyword to filter results.  
    :return: Filtered results based on keyword relevance.  
    """  
    return [result for result in results if keyword.lower() in result['snippet'].lower()]  
