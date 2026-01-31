import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup # to scrape the web page
from urllib.parse import urldefrag # to separate the domain and fragment in url

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    list = []
    visited = set()

    visited.add(resp) # add the seed url first
    
    if resp.status != 200: # if the resp page is not valid 
        print(resp.error) # checking the error if resp page is invalid
        return list()
    
    # if the page is valid
    page_content = BeautifulSoup(resp.raw_response.content, "lxml")
    
    # extract all links in the page
    for link in page_content.find_all('a', href=True):
        
        cur_link = link.get('href') 
        
        # if the link on the page is valid, add it to the list
        if is_valid(cur_link) and cur_link not in visited:
            print(cur_link)
            list.append(cur_link)
            visited.add(cur_link)

    print(len(visited)) # count of unique page
    return list

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    ALLOWED_DOMAINS = ("ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu")
    try:
        url, frag = urldefrag(url) # defragment the fragment portion in url
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if not parsed.netloc.endswith(ALLOWED_DOMAINS): # only accepts tuple that's why i use tuple for allowed domain
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
