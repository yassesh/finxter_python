import pinecone
import openai
from dotenv import dotenv_values
config = dotenv_values(".env")

pinecone.init(api_key= config["PINECONE_KEY"],
              environment="us-west4-gcp-free")

index = pinecone.Index("chris")

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def addData(web_data,url):
    id  = index.describe_index_stats()['total_vector_count']
    for i in range(len(web_data)):
        chunk=web_data[i]
        chunkInfo=(str(id+i),
                get_embedding(chunk,model="text-embedding-ada-002"),
                {'title': url,'context': chunk})
        index.upsert(vectors=[chunkInfo])

def find_match(query,k):
    query_em = get_embedding(query,model= "text-embedding-ada-002")
    result = index.query(query_em, top_k=k, includeMetadata=True)
    
    return [result['matches'][i]['metadata']['title'] for i in range(k)],[result['matches'][i]['metadata']['context'] for i in range(k)]
     