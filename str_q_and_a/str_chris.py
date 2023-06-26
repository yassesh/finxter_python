import streamlit as st
from embedding_search import *
import prompt_generator
from text_extractor import *

st.header("SEARCH ANY WEBPAGE WITH ME")
url = False
query = False
options = st.radio(
    'Choose task',
    ("Ask me a question",'Update the Database'))

if 'Update the Database' in options:
    url = st.text_input("Enter the url of the document")
    
if 'Ask me a question' in options:
    query = st.text_input("Enter your question")

button = st.button("Submit")
  
if button and (url or query):
    if 'Update the Database' in options:
        with st.spinner("Updating Database..."):
            webdata = scrape_text_from_url(url)
            addData(webdata,url)
            st.success("Database Updated")
    if 'Ask me a question' in options:
        with st.spinner("Searching for the answer..."):
            urls,res = find_match(query,1)
            context= "\n\n".join(res)
            st.expander("Context").write(context)
            prompt = prompt_generator.create_prompt(context,query)
            answer = prompt_generator.generate_answer(prompt)
            st.success("Answer: "+answer)
