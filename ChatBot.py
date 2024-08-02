import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from openai import OpenAI
from ResponseGetters import get_response, get_default_agent_response, get_custom_response, get_plot_response
from DynamicAgent import get_dynamic_agent_response
from streamlit_pills import pills
from streamlit_extras.stylable_container import stylable_container
import os

#Set OpenAI Key to access llm
os.environ["OPENAI_API_KEY"] = ""

#Set LangSmith Keys for tracing
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = ""
# os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
# os.environ["LANGCHAIN_PROJECT"]=""

#############Page Setup
#set_page_config must be first streamlit command, called once per page
st.set_page_config(page_title="SQL ChatBot", page_icon="🤖", layout='centered')
st.title("SQL ChatBot")
user_query  = st.chat_input("Enter your question")

#Sidebar for chatbot selection
sideb = st.sidebar
choosebot = sideb.selectbox(
    "Pick Chatbot version",
    ("Default", "Default-Agent", "Custom", "Dynamic-Agent"),
    index=0,
    help ="**Default**: Flakiest  \n**Custom**: Improved Default that remembers chat history  \n**Default-Agent**: Returns thinking proccess and query  \n**Dynamic-Agent**: Improved Default-Agent, remembers history, most robust"
)

sideb.markdown("""---""")

#Adding about to sidebar
with sideb.expander("About SQL ChatBot"):
    st.write('''
        This chatbot converts user questions into SQL queries, returning database output as a natural language response.
             View the Dashboard sidebar for more information about the datasets.
             
        View the code on [GitHub]("https://github.com/mangocheeks/sqlchatbot/blob/main/README.md")
    ''')

#Create a chat history if not already existed
#Add default message
if "chat_history" not in st.session_state:
    st.session_state.chat_history =[]
    infomsg='Ask me something about the Zara, Walmart, or Adidas sales datasets'
    st.session_state.chat_history.append(AIMessage(infomsg))

#Show stored chat history on each rerun
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

#Create pill suggestions with bottom formatting

#Pill formatting currently has css issues with it showing in front of messages
#So suggestions can only be clicked once a session
placeholder = st.empty()

with placeholder.container():

    with stylable_container(
    key="bottom_content",
    css_styles="""
        {
            position: fixed;
            bottom: 105px;
        }
        """,
    ):
        selected = pills("Here are some suggested prompts:",
                        ["What is the highest rated walmart branch on average?", 
                        "Tell me about the tables in the database",
                        "Which adidas retailer had the most total sales in January?"],
                        index=None
                        )

if "choose_suggested" not in st.session_state:
    st.session_state.choose_suggested = False

#Hide suggestions after selecting one or if no prompt was picked at first
if selected is not None:
    #if selection not made before, assign to user input
    if st.session_state.choose_suggested == False:
        user_query = selected

    st.session_state.choose_suggested = True
    #Empty will hide the pills for the rest of the session but selected will retain its value unless reassigned
    #Hence double check using choose_suggested
    placeholder.empty()

#Get Response
if user_query is not None and user_query !="":
    #add message to history
    st.session_state.chat_history.append(HumanMessage(user_query))

    #Hide suggestion prompts if no suggestion was made as the very first prompt
    if (st.session_state.chat_history.__len__()) > 1 and st.session_state.choose_suggested == False:
        placeholder.empty()

    with st.chat_message("Human"):
        #display message in markdown
        st.markdown(user_query)

    with st.spinner("Generating response"):
        with st.chat_message("AI"):
            #Choose bot based on selection
            
            if choosebot == "Custom":
                ai_response = get_custom_response(user_query, st.session_state.chat_history)
                st.markdown(ai_response)
            elif choosebot == "Default-Agent":
                ai_response = get_default_agent_response(user_query)
                st.markdown(ai_response)
            elif choosebot == "Default":
                ai_response=st.write_stream(get_response(user_query))
            else:
                ai_response=get_dynamic_agent_response(user_query, st.session_state.chat_history)
                st.markdown(ai_response)

    st.session_state.chat_history.append(AIMessage(ai_response))
    print(st.session_state.chat_history)

#Hide suggestion prompts if no suggestion was made as the very first prompt
if (st.session_state.chat_history.__len__()) > 1 and st.session_state.choose_suggested == False:
    placeholder.empty()