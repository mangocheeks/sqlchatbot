from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from Prompts import examples, format_examples, table_info, graphexamples

#used for get_custom_response
answer_prompthist = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, chat history, and SQL result, answer the user question. Check that the final answer logically answer the user's question. If it does not, explain why you need 
clarificaiton and cannot currently answer the question. Format the output to be viewable for markdown. For instance, the '$'
character needs to be written as '\$'

Chat history to reference: {chat_history}
Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

#used for get_custom_response
custom_prompt = PromptTemplate.from_template(
    """You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run,
    then look at the results of the query and return the answer to the input question.
    
    When building the query, keep in mind the following points:
    - Your SQL Query should contain ONE SELECT statement
    - If it is not possible to answer the query with one select statement, pick the select statement that gets new information not already found in chat_history
    - Reference the chat history and provided examples
    - Unless the user specifies in the question a specific number of examples to obtain, query for at most 5 results using the LIMIT clause as per SQLite
    - You can order the results to return the most informative data in the database
    - Query only the columns that are needed to answer the question
    - Wrap each column name in double quotes (") to denote them as delimited identifiers
    - Pay attention to use only the column names you can see in the tables below
    - Be careful to not query for columns that do not exist
    - Also, pay attention to which column is in which table.
    - When ordering and calculating sums of numerical values, convert the column to a numerical data type to proccess correctly
    - Double check that your SQL query has only one select statement
    - If it is not possible to answer the query with one select statement, pick the select statement that gets new information not already found in chat_history

Use the following format:

Question: Question here
SQL Query: SQL Query to run 

Only use the following tables: {table_info}

Chat history to reference: {chat_history}

Here are a number of examples of questions and their corresponding SQL queries: 
{examples}

Question: {question}

Your format your output to look like this:

SQL Query: 

"""
)

#used for get_default_response
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question. Check that the final answer logically answer the user's question. If it does not, explain why you need 
clarificaiton and cannot currently answer the question. Format the output to be viewable for markdown.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

#used for get_plot_response
plot_prompt = PromptTemplate.from_template(
    """You are an expert on pandas python library. Given a SQL query that retrieves information from the sales database, create a syntactically
    correct Python script to build a streamlit graph from the output. Use the examples as a reference. Use the following template and modify the 
    code section as needed. The code should start with ```python and end with ```

Examples: {examples}
Question: {question}

Code:
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

query = {query}
conn = create_engine("sqlite:///sales.db")
#Read query data
#This line is REQUIRED:
query_data = pd.read_sql_query({query}, conn)

    #Create dataframe from query data and fill in with columns based on query
    #This line is REQUIRED:
    df = pd.DataFrame(query_data, columns= [_________])

    #Streamlit chart declaration here"""
)

#Takes static few shots
#Get two arguments to run plot response via textboxes
def get_plot_response(query, question):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    chain = plot_prompt | llm | StrOutputParser()

    return chain.invoke({
        "examples": graphexamples,
        "question": query,
        "query": question,
    })

def clean_sql_query(query_output):
    return query_output.replace("SQL Query: ", "").strip()

#Custom prompt with history and static few shot prompt
#run with databasetool to get correct output, ai itself cannot access it directly
def get_custom_response(query, chat_history):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    dbname="sqlite:///sales.db"
    db = SQLDatabase.from_uri(dbname)

    chain = custom_prompt | llm | StrOutputParser()
    execute_query = QuerySQLDataBaseTool(db=db)    

    masterchain = (
    RunnablePassthrough.assign(query=chain).assign(
        #sql query is stored in query key for execute_query after being stripped
        #result key is stored from execute_query to be fed into answer_prompt
        #specifying all keys/context neccesary
        result=lambda context: execute_query.invoke({"query": clean_sql_query(context["query"])})
    )
    | (lambda context: answer_prompthist.invoke({
        "question": context["question"],
        "query": clean_sql_query(context["query"]),
        "result": context["result"],
        "chat_history": context["chat_history"]
    })) | llm | StrOutputParser()
    )

    #feed inputs for head of chain
    return masterchain.invoke(
        {
            "table_info": table_info,
            "examples": format_examples(examples),
            "chat_history": chat_history,
            "question": query,
        }
    )


#Agents supprort error handling and chain of thought prompting
def get_default_agent_response(query):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    dbname="sqlite:///sales.db"
    db = SQLDatabase.from_uri(dbname)

    print("Getting agent response")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent_executor = create_sql_agent(
    llm=llm,
    streaming=True,
    toolkit=toolkit,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
    handleParsingErrors=
    "Please try again, paying close attention to the allowed input values",
    verbose=True
    
    )
    
    #Callback allows agents to strean
    st_callback = StreamlitCallbackHandler(st.container())
    response = agent_executor.run(query, callbacks=[st_callback])
    return response

#simplest reponse generator with sql_query_chain, execution with SQL database tool
#and chained with natural language prompt
#no memory
def get_response(query):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    dbname="sqlite:///sales.db"
    db = SQLDatabase.from_uri(dbname)

    print("Getting chain")
    write_query = create_sql_query_chain(llm, db)
    #allows query output to be viewed separately and troubleshooted with
    #langchain
    execute_query = QuerySQLDataBaseTool(db=db)
    answer = answer_prompt | llm | StrOutputParser()
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
    )
    #chain.stream returns the text as it is being generated for smoother ux feel
    return chain.stream({"question": query})