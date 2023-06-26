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
