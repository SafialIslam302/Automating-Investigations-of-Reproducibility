from bs4 import BeautifulSoup
import requests
from fuzzywuzzy import fuzz
import re


def check_original_repository(url, lowercase_search_string, modify_lowercase_one_search_string,
                              modify_lowercase_two_search_string):
    # Send a GET request to the URL
    response = requests.get(url)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the text on the webpage
    page_text = soup.get_text()

    # Convert the page text to lowercase
    lowercase_page_text = page_text.lower()

    # remove all special character from the website text
    pattern = r'[^a-zA-Z0-9\s]'

    # clean the blank space for the special character
    cleaned_text = re.sub(pattern, '', lowercase_page_text)

    case_one = lowercase_search_string.lower()
    case_two = modify_lowercase_one_search_string.lower()
    case_three = modify_lowercase_two_search_string.lower()

    # Calculate the similarity ratio
    similarity_ratio = fuzz.partial_ratio(cleaned_text, case_one) / 100
    similarity_ratio_one = fuzz.partial_ratio(cleaned_text, case_two) / 100
    similarity_ratio_two = fuzz.partial_ratio(cleaned_text, case_three) / 100

    # Check if the similarity ratio is at least 90%
    if (case_one in cleaned_text or case_two in cleaned_text
            or case_three in cleaned_text or similarity_ratio >= 0.9
            or similarity_ratio_one >= 0.9 or similarity_ratio_two >= 0.9):
        print(
            f"String '{case_one}' or {case_two} or "
            f"{case_three} found in URL: {url} "
            f"(Similarity: {similarity_ratio} or {similarity_ratio_one} or {similarity_ratio_two})"
        )
        return True, url, similarity_ratio

    return False, None, None
