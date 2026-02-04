import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup # to scrape the web page
from urllib.parse import urljoin,urldefrag # to separate the domain and fragment in url
from collections import Counter 

# Adding stopwords
STOP_WORDS = set()
try:
    with open('stopwords.txt', 'r') as f:
        for line in f:
            STOP_WORDS.add(line.strip().lower())
    
except FileNotFoundError:
    print("stopwords.txt not found")
    
def scraper(url, resp):
   
   # For text content on the page
    if resp.status != 200 or not resp.raw_response:
        return []
        
    # size check: if file is huge, ignore the page
    # general limit size for web pages is ~3MB
    if len(resp.raw_response.content) > 3_000_000:
        return []

    # check the content type header
    # we have to check if the page is html and not pdf, images, and other types
    content_type = resp.raw_response.headers.get('Content-Type', '').lower()
    
    if "text/html" not in content_type:
        return []
    
    try:
         # Parse html to get plain text
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')

        # Remove non-visible / non-content elements (e.g javascript/css style texts)
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "meta", "link", "title", "input"]):
            tag.decompose()

        text_content = soup.get_text(separator=" ", strip=True)
        
        # Tokenize using simple Regex 
        words = re.findall(r'[a-zA-Z0-9]+', text_content.lower())
        
        # Filter out stop words and single letters (like 'a', 'i')
        filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 1]
        
        # save to stats.txt for the final report
        # we want to crawl all pages with high textual information content
        if len(filtered_words) >= 50:
        
            # format - url | num of words on that url | text on that url
            with open("stats.txt", "a", encoding="utf-8") as f:
                words_string = " ".join(filtered_words)
                f.write(f"{url}\t{len(filtered_words)}\t{words_string}\n")

        # if the words is < 50, we don't save the text content in our log. We just proceed to extract links.
    except Exception as e:
        print(f"Error processing text for {url}: {e}")
    
    # For links on the page
    links = extract_next_links(url, resp)
    links = [link for link in links if is_valid(link)]
    print(f"Found {len(links)} valid links on {url}")
    return links

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
    links = set()
   
    if resp.status != 200: # if the resp page is not valid 
        print(resp.error) # checking the error if resp page is invalid
        return list(links)
    
    # if the page is valid
    page_content = BeautifulSoup(resp.raw_response.content, "lxml")
    
    # extract all tags/paths in the page
    for tag in page_content.find_all('a', href=True):
        
        # removing fragment part of the url links
        cur_tag = tag["href"]
        abs_url = urljoin(url, cur_tag)
        abs_url, frag = urldefrag(abs_url)
        
        # handling duplicates 
        # (https://www.ics.uci.edu is the same as "https://ics.uci.edu")
        parsed = urlparse(abs_url)
        netloc = parsed.netloc.replace("www.", "")
        
        # remove trailing slash from the path to avoid duplicates like https://ics.uci.edu/about/ vs https://ics.uci.edu/about
        path = parsed.path
        if path.endswith('/'):
            path = path.rstrip('/')
            
        # reconstruct the url
        # we force 'https' so http://ics.uci.edu and https://ics.uci.edu are the same
        new_parsed = parsed._replace(netloc = netloc, path=path, scheme='https')
        final_url = new_parsed.geturl()
        
        links.add(final_url)
       
    return list(links)

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

        # Trap detection
        # filter out apache indexes or duplicate pages that differ only by sorting parameters (the same page content but diffent url name)
        # e.g. https://ics.uci.edu/~dechter/softwares/benchmarks/Mmap_Problem_Sets?C=D;O=D and https://ics.uci.edu/~dechter/softwares/benchmarks/Mmap_Problem_Sets?C=D;O=A
        if parsed.query and "C=" in parsed.query and "O=" in parsed.query:
            return False
            
        # Block the UCI Machine Learning Repository explicitly
        if "archive.ics.uci.edu" in parsed.netloc:
            return False
        
        # Block calendar/date traps
        if re.search(r"/\d{4}/\d{2}/\d{2}", parsed.path): # YYYY/MM/DD
            return False
        
        if any(x in parsed.path.lower() for x in ["calendar", "event", "events"]): # /events/ /calendar/ /upcoming-events/
            return False
        
        # check the query contain page, month, and year
        if any(x in parsed.query.lower() for x in ["page=", "month=", "year="]):
            return False

        # if the URL is too long, can be a trap
        if len(url) > 100:
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
