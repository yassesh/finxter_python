from tweety.bot import Twitter
import re
import json
from datetime import datetime
from typing import Dict, List

import pandas as pd
import streamlit as st
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tweety.types import Tweet
import os

# import openai
# from dotenv import dotenv_values
# config = dotenv_values(".env")
# openai.api_key = config["OPENAI_API_KEY"]


twitter_client = Twitter()
# tweets = twitter_client.get_tweets("hwchase17")

# for tweet in tweets:
#     print(tweet.id)
#     print(tweet.text)
#     print()

def clean_tweet(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www.\S+", "", text)
    text = re.sub(r"b'\S+", "", text)
    text = re.sub(r'b"\S+', "", text)
    return re.sub(r"\s+", " ", text)

# for tweet in tweets:
#     print(tweet.id)
#     print("uncleaned")
#     print(tweet.text.encode("utf-8"))
#     print('cleaned')
#     encoded_tweet = str(tweet.text.encode("utf-8"))
#     print(clean_tweet(encoded_tweet))

def create_dataframe_from_tweets(tweets: List[Tweet]) -> pd.DataFrame:
    rows = []
    for tweet in tweets:
        tweet_string = str(tweet.text.encode("utf-8"))
        clean_text = clean_tweet(tweet_string)
        if len(clean_text) == 0:
            continue
        rows.append(
            {
                "id": tweet.id,
                "text": clean_text,
                "author": tweet.author.username,
                "date": str(tweet.date.date()),
                "created_at": tweet.date,
                "views": tweet.views,
            }
        )    
    df = pd.DataFrame(
        rows, columns=["id", "text", "author", "date", "views", "created_at"]
    )
    df.set_index("id", inplace=True)
    if df.empty:
        return df
    df = df[df.created_at.dt.date > datetime.now().date() - pd.to_timedelta("7day")]
    return df.sort_values(by="created_at", ascending=False)

# print(create_dataframe_from_tweets(tweets))

st.set_page_config(
    layout="wide",
    page_title="Investor Twitter Sentiment Analysis",
)

st.title('Cryptogpt')

def on_add_author():
    # print(st.session_state.twitter_handle)
    twitter_handle = st.session_state.twitter_handle
    if twitter_handle.startswith("@"):
        twitter_handle = twitter_handle[1:]
    if twitter_handle in st.session_state.twitter_handles:
        return
    all_tweets = twitter_client.get_tweets(twitter_handle)
    if len(all_tweets) == 0:
        return
    st.session_state.twitter_handles[twitter_handle] = all_tweets[0].author.name
    st.session_state.tweets.extend(all_tweets)
    # st.session_state.author_sentiment[twitter_handle] = analyze_sentiment(
    #     twitter_handle, st.session_state.tweets
    # )


if not "tweets" in st.session_state:
    st.session_state.tweets = []
    st.session_state.twitter_handles = {}
    st.session_state.api_key = ""
    # st.session_state.author_sentiment = {}

os.environ["OPENAI_API_KEY"] = st.session_state.api_key

print(st.session_state.api_key)

col1, col2 = st.columns(2)
with col1:
    st.text_input(
        "OpenAI API Key",
        type="password",
        key="api_key",
        placeholder="sk-...4242",
        help="Get your API key: https://platform.openai.com/account/api-keys",
    )
    with st.form(key="twitter_handle_form", clear_on_submit=True):
        st.subheader("Add Twitter Accounts", anchor=False)
        st.text_input(
            "Twitter Handle", value="", key="twitter_handle", placeholder="@input_tweetHandler"
        )
        submit = st.form_submit_button(label="Add Tweets", on_click=on_add_author)
    if st.session_state.twitter_handles:
        st.subheader("Twitter Handles", anchor=False)
        for handle, name in st.session_state.twitter_handles.items():
            handle = "@" + handle
            st.markdown(f"{name} ([{handle}](https://twitter.com/{handle}))")

    st.subheader("Tweets", anchor=False)
    st.dataframe(
        create_dataframe_from_tweets(st.session_state.tweets), use_container_width=True
    )
