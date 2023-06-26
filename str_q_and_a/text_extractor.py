import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_html_content(url):
    response = requests.get(url)
    return response.content

def remove_newlines(text):
    cleaned_text = text.replace('\n', '')
    return cleaned_text

def get_plain_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script"]):
        script.extract()
    return soup.get_text()

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 2000)

def scrape_text_from_url(url):
    html_content = get_html_content(url)
    plain_text_with_newline = get_plain_text(html_content)
    plain_text = remove_newlines(plain_text_with_newline)
    splitted_text = text_splitter.split_text(plain_text)
    return splitted_text


