import requests
from bs4 import BeautifulSoup

# Function to search Bing for relevant websites
def search_bing(query, api_key, endpoint="https://api.bing.microsoft.com/v7.0/search", num_results=10):
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": num_results}
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    results = response.json()
    return [result["url"] for result in results.get("webPages", {}).get("value", [])]

# Function to extract textual content from a webpage
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract visible text
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text() for p in paragraphs if p.get_text())
        return content.strip()
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

# Main workflow
def get_relevant_texts(query, api_key):
    success = 0
    print(f"Searching for: {query}")
    urls = search_bing(query, api_key)

    print("\nRetrieved URLs:")
    for url in urls:
        print(url)

    texts = []
    for url in urls:
        print(f"\nScraping: {url}")
        text = scrape_website(url)
        if text:
            print(text[:100])
            if len(text) > 10000 :
                text = text[:10000]
            texts.append(text)
            success += 1
        if success >= 3 :
            break
    return texts