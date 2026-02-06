"""
This is for answering the questions of the assignment. 
"""

def uniquePage():
    """
    Description:
    Since our stats.txt file contains valid unique url pages that are allowed to crawl, we need to 
    open our stats.txt file and count the links

    param:

    return(int): 
    count of lines in stats.txt
    """
    count = 0
    with open('stats.txt', 'r') as f:
        for url in f:
            count += 1
    return count

def getLongestPage():
    pass

def getCommonWords():
    pass

def getSubdomainList():
    pass

def main():
    num_of_unique_page = uniquePage()
    print(f"Num of unique pages: {num_of_unique_page}")

if __name__ == "__main__":
    main()