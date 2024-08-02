from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from Prompts import examples
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

import os

#Set API Key
os.environ["OPENAI_API_KEY"] = ""

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    Chroma,
    k=3,
    input_keys=["input"],
)

#test example selector
#example_selector.select_examples({"input": "what are the top 10 mosy purchazed items from zara?"})

#agent dynamic few shot prompt
#https://python.langchain.com/v0.1/docs/use_cases/sql/agents/#using-a-dynamic-few-shot-prompt


system_prefix = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Make sure the final SQL query is properly formatted with no triple backticks or unpaired quotation marks
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the question does not seem related to the database, just return "I don't know" as the answer.

Here is the chat history for reference when buliding your query: {chat_history}

Here are some examples of user inputs and their corresponding SQL queries:"""

few_shot_prompt = FewShotPromptTemplate(
    #assigns dynamic few shot selector
    example_selector=example_selector,
    #Creates prompt
    example_prompt=PromptTemplate.from_template(
        "User input: {input}\nSQL query: {query}"
    ),
    input_variables=["input", "dialect", "top_k", "chat_history"],
    #sets more text before prompt
    prefix=system_prefix,
    suffix="",
)

full_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(prompt=few_shot_prompt),
        ("human", "{input}" "{chat_history}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)
#Call sql agent with dynamic few shot and history
def get_dynamic_agent_response(query, chat_history):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    dbname="sqlite:///sales.db"
    db = SQLDatabase.from_uri(dbname)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    prompt=full_prompt,
    verbose=True,
    handle_parsing_errors=True,
    streaming=True,
    agent_type="openai-tools",
    )
    
    st_callback = StreamlitCallbackHandler(st.container())
    #agent run can accept explicitly declared context keys
    response = response = agent.run(
        input=query,
        chat_history=chat_history,
        callbacks=[st_callback]
    )
    return response