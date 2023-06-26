from tweety.bot import Twitter
import re
from typing import List,Dict
import pandas as pd
from tweety.types import Tweet
from datetime import datetime , timedelta
import streamlit as st
import os
import plotly.express as px
from trader_sentiment import create_dataframe_from_tweets , analyze_sentiment

twitter_client = Twitter()

# for tweet in tweets:
#     print(tweet.id)
#     tweet_string = str(tweet.text.encode("utf-8"))
#     print(clean_tweet(tweet_string))
#     print()

st.set_page_config(
        layout= "wide",
        page_title= "Trader Sentiment"
    )
st.title('Trader Sentiment Analysis')

import re
from typing import List,Dict
import pandas as pd
from tweety.types import Tweet
from datetime import datetime
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json

PROMPT_TEMPLATE = """
You're a cryptocurrency trader with 10+ years of experience. You always follow the trend
and follow and deeply understand crypto experts on Twitter. You always consider the historical predictions for each expert on Twitter.

You're given tweets and their view count from @{twitter_handle} for specific dates:

{tweets}

Tell how bullish or bearish the tweets for each date are. Use numbers between 0 and 100, where 0 is extremely bearish and 100 is extremely bullish.
Use a JSON using the format:

date: sentiment

Each record of the JSON should give the aggregate sentiment for that date. Return just the JSON. Do not explain.
"""

def clean_tweet(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www.\S+", "", text)
    text = re.sub(r"b'\S+", "", text)
    text = re.sub(r'b"\S+', "", text)
    return re.sub(r"\s+", " ", text)

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
        rows, columns=["id", "text", "author", "date", "views", "created_at"] )
    
    df.set_index("id", inplace=True)
    if df.empty:
        return df
    df = df[df.created_at.dt.date > datetime.now().date() - pd.to_timedelta("7day")]
    return df.sort_values(by="created_at", ascending=False)

def create_tweet_list_for_prompt(tweets: List[Tweet], twitter_handle: str) -> str:
    df = create_dataframe_from_tweets(tweets)
    user_tweets = df[df.author == twitter_handle]
    if user_tweets.empty:
        return ""
    if len(user_tweets) > 100:
        user_tweets = user_tweets.sample(n=100)
    text = ""

    for tweets_date, tweets in user_tweets.groupby("date"):
        text += f"{tweets_date}:"
        for tweet in tweets.itertuples():
            text += f"\n{tweet.views} - {tweet.text}"
    return text


def analyze_sentiment(twitter_handle: str, tweets: List[Tweet]) -> Dict[str, int]:
    chat_gpt = ChatOpenAI(temperature=0, model= "gpt-3.5-turbo")
    prompt = PromptTemplate(
        input_variables= ["twitter_handle","tweets"], template= PROMPT_TEMPLATE
    )
    sentiment_chain = LLMChain(llm= chat_gpt, prompt= prompt)
    response = sentiment_chain(
        {
            "twitter_handle": twitter_handle,
            "tweets": create_tweet_list_for_prompt(tweets, twitter_handle),            
        }
    )

    return json.loads(response["text"])

if not "tweets" in st.session_state:
    st.session_state.tweets = []
    st.session_state.api_key = ""
    st.session_state.twitter_handles = {}
    st.session_state.author_sentiment = {}

os.environ["OPENAI_API_KEY"] = st.session_state.api_key

def on_add_author():
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
    st.session_state.author_sentiment[twitter_handle] = analyze_sentiment(
        twitter_handle, st.session_state.tweets
    )

def create_sentiment_dataframe(sentiment_data: Dict[str, int]) -> pd.DataFrame:
    date_list = pd.date_range(
        datetime.now().date() - timedelta(days=6), periods=7, freq="D"
    )
    dates = [str(date) for date in date_list.date]
    chart_data = {"date": dates}

    for author, sentiment_data in sentiment_data.items():
        author_sentiment = []
        for date in dates:
            if date in sentiment_data:
                author_sentiment.append(sentiment_data[date])
            else:
                author_sentiment.append(None)
        chart_data[author] = author_sentiment
    
    sentiment_df = pd.DataFrame(chart_data)
    sentiment_df.set_index("date", inplace=True)

    if not sentiment_df.empty:
        sentiment_df["Final Score"] = sentiment_df.mean(skipna=True, axis=1)

    return sentiment_df





col1, col2 = st.columns(2)

with col1:
    st.text_input("OpenAI API KEY", type= "password",key="api_key",
        placeholder="Enter your API key",
        help="Get your API key: https://platform.openai.com/account/api-keys",)
    
    with st.form(key="twitter_handle_form", clear_on_submit=True):
        st.subheader("Add Twitter Accounts", anchor=False)
        st.text_input(
            "Twitter Handle", value="", key="twitter_handle", placeholder="@input_tweetHandler"
        )
        submit = st.form_submit_button(label="Add Tweets", on_click= on_add_author)
    
    if st.session_state.twitter_handles:
        st.subheader("Twitter Handles", anchor=False)
        for handle, name in st.session_state.twitter_handles.items():
            handle = "@" + handle
            st.markdown(f"{name} ([{handle}](https://twitter.com/{handle}))")

    st.subheader("Tweets", anchor=False)
    st.dataframe(
        create_dataframe_from_tweets(st.session_state.tweets), use_container_width=True
    )
    #st.markdown(st.session_state.author_sentiment)

with col2:
    sentiment_df = create_sentiment_dataframe(st.session_state.author_sentiment)
    if not sentiment_df.empty:
        fig = px.line(
            sentiment_df,
            x = sentiment_df.index,
            y = sentiment_df.columns,
            labels= {"date": "Date" , "value" : "Sentiment"}
        )
        fig.update_layout(yaxis_range = [0,100])
        st.plotly_chart(fig,theme="streamlit", use_container_width= True)    
        st.dataframe(sentiment_df, use_container_width= True)

# print(create_dataframe_from_tweets(tweets))