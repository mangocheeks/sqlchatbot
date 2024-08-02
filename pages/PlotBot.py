import streamlit as st
from ResponseGetters import get_plot_response
import os

#set openai key
os.environ["OPENAI_API_KEY"] = ""

#Set LangSmith keys for tracing
# os.environ["LANGCHAIN_TRACING_V2"] = ""
# os.environ["LANGCHAIN_API_KEY"] = ""
# os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
# os.environ["LANGCHAIN_PROJECT"]=""

#Page setup
st.set_page_config(page_title="PlotBot", page_icon="🤖", layout='centered')

#Sidebar about info
sideb = st.sidebar
with sideb.expander("About PlotBot"):
    st.write('''
        This is an experimental chatbot that takes a SQL query and user input to generate Python code of graphed data.
    ''')

#get two arguments to run plot response via textboxes
if "query_input" not in st.session_state:
    st.session_state.query_input=""
if "question_input" not in st.session_state:
    st.session_state.question_input=""

#Put inside container
prompt = st.container(border=True)
with prompt:
    st.title("PlotBot") 
    st.markdown("##### (Experimental)")
    query_input = st.text_input("Enter SQL query")
    question_input = st.text_input("Enter question")

#needs ()
after = st.container()

def call():
    #check both boxes have content before launching
    if query_input and question_input:
        #st.write("running")
        response = get_plot_response(query=query_input, question=question_input)
        with after:
            st.markdown(response)
    else:
        with after:
            st.write("Both boxes need valid input")
    
with prompt:
    st.button("Launch Query", on_click=call)
    #do not use on_click=call()! it will run on page refresh/load