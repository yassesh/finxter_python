from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
import os 

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = OpenAI()


template = """
Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done,there will be 21 trees. How many trees did the grove workers plant today?
A: We start with 15 trees. Later we have 21 trees. The difference must be the number of trees they planted. So, they must have planted 21 - 15 = 6 trees. The answer is 6.

Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?
A: There are 3 cars in the parking lot already. 2 more arrive. Now there are 3 + 2 = 5 cars. The answer is 5.

Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?
A: Leah had 32 chocolates and Leah’s sister had 42. That means there were originally 32 + 42 = 74 chocolates. 35 have been eaten. So in total they still have 74 - 35 = 39 chocolates. The answer is 39.

Q: When I was 6 my sister was half my age. Now I’m 70 how old is my sister?
A:

"""

prompt = PromptTemplate(
    input_variables=[],
    template=template
)

llm = OpenAI()
chain = LLMChain(llm=llm, prompt=prompt)

print("### Model Output ###")
for i in range(3):
  print(f"Output {i+1}\n {chain.predict()}")
