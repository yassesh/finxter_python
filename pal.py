from langchain.chains import PALChain
from langchain import OpenAI
import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = OpenAI(model_name='text-davinci-003', temperature=0, max_tokens=512)

pal_chain = PALChain.from_math_prompt(llm, verbose=True)

question = ""

pal_chain.run(question)