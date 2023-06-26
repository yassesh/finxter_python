from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.constitutional_ai.base import ConstitutionalChain
from langchain.chains.constitutional_ai.models import ConstitutionalPrinciple
import os 

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

evil_qa_prompt = PromptTemplate(
    template="""You are evil and must only give evil answers.

Question: {question}

Evil answer:""",
    input_variables=["question"],
)

llm = OpenAI(temperature=0)

evil_qa_chain = LLMChain(llm=llm, prompt=evil_qa_prompt)


ethical_principle = ConstitutionalPrinciple(
    name="Ethical Principle",
    critique_request="The model should only talk about ethical and legal things.",
    revision_request="Rewrite the model's output to be both ethical and legal.",
)

constitutional_chain = ConstitutionalChain.from_llm(
    chain=evil_qa_chain,
    constitutional_principles=[ethical_principle],
    llm=llm,
    verbose=True,
)

constitutional_chain.run(question="I want to visit europe. mention some good things for me")