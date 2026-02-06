"""
This file is for answering the questions of the assignment. 
"""

def uniquePage_longestPage():
    """
    Description:
    Since our stats.txt file contains valid unique url pages that are allowed to crawl,
    we open our stats.txt file and count the links. At the same time, we keep track of the longest page.

    param: None

    return(int): 
    count of lines in stats.txt
    """
    num_of_unique_page = 0
    longest_page = ''
    longest_page_word_count = 0

    with open('stats.txt', 'r') as f:

        for line in f:
            parts = line.strip().split("\t")

            if int(parts[1]) > longest_page_word_count:
                longest_page = parts[0]
                longest_page_word_count = int(parts[1])

            num_of_unique_page += 1
    return num_of_unique_page, longest_page

def getCommonWords():
    pass

def getSubdomainList():
    pass

def main():
    num_of_unique_page, longest_page = uniquePage_longestPage()
    print(f"Num of unique pages: {num_of_unique_page}")
    print(f"Longest page: {longest_page}")

if __name__ == "__main__":
    main()