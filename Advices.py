from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Bedrock
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from langchain.chains.question_answering import load_qa_chain
from langchain import PromptTemplate

import warnings

import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

import os.path
import pathlib

from data_loader import load

import sqlite3

# Settings the warnings to be ignored
warnings.filterwarnings('ignore')

with open("./config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

embeddings = HuggingFaceEmbeddings()


def get_llm():
    llm = Bedrock(
        credentials_profile_name="lemonstudio",
        model_id="anthropic.claude-instant-v1",
        model_kwargs={'max_tokens_to_sample': 2000, 'temperature': 0},
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]
    )
    return llm


def get_methodology_answer(query, weight=4):
    parent_path = pathlib.Path(__file__).parent.resolve()
    user_path = os.path.join(parent_path, "embedding_methodology")
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=user_path
    )
    return vectordb.similarity_search(query, k=weight)


def get_project_answer(query, project, weight=4):
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory="/Users/alex/dev/deanx/ia/langchain-pdf/pdf1/bedrock_embeddings"
    )
    return vectordb.similarity_search(query, k=weight)


def get_technical_answer(query, weight=2):
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory="/Users/alex/dev/deanx/ia/langchain-pdf/pdf1/stored"
    )
    return vectordb.similarity_search(query, k=weight)


def generate_response(message, project, role="Advisor"):
    
    if role == "Advisor":
        prompt_template = """Use ONLY the following pieces of context to answer the question at the end. 
        If you cannot find the answer in the following context, just say that you don't know, don't try to make up an answer.
        {context}
        Assuming your are a Strategic Advisor, answer the following question:
        Question: {question}
        """

        project_docs = list(get_project_answer(message, project, 4))
        methodology_docs = list(get_methodology_answer(message, 4))
        tech_docs = list(get_technical_answer(message, 2))

    else:
        prompt_template = """Use ONLY the following pieces of context to answer the question at the end. 
            If you cannot find the answer in the following context, just say that you don't know, don't try to make up an answer.
            {context}
            Assuming your are a Software Implementation Architect, answer the following question:
            Question: {question}
            """
        project_docs = list(get_project_answer(message, project, 4))
        methodology_docs = list(get_methodology_answer(message, 4))
        tech_docs = list(get_technical_answer(message, 2))

    final_docs = project_docs + methodology_docs + tech_docs
        
    
    return ""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain = load_qa_chain(get_llm(), chain_type="stuff", prompt=PROMPT)

    response = chain({"input_documents": final_docs, "question": message},
                     return_only_outputs=True)

    return response["output_text"]


if "authentication_status" not in st.session_state or st.session_state["authentication_status"] == None:
    st.session_state["authentication_status"] = None
    st.info('Please enter your username and password')

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    col1, col2 = st.columns(2)
    with col1:
        st.write(f'Welcome *{name}*')
    with col2:
        authenticator.logout('Logout', 'main')
    st.divider()


elif authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()

if "authentication_status" not in st.session_state or st.session_state["authentication_status"] == None:
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def on_input_change():
    input = st.session_state.user_input
    chat_role = st.session_state.chat_role
    project = st.session_state.chat_project
    
    if len(input) < 10:

        st.toast("Need more than 10 characters to throw a question")
        return
    response = generate_response(st.session_state.user_input, project, chat_role)

    st.session_state.messages.append({"role": "user", "content": input})
    st.session_state.messages.append(
        {"role": "assistant", "content": response})


with sqlite3.connect("projects.db") as connection:
    cursor = connection.cursor()
    query = cursor.execute("select project from projects where username='" + username + "'")
    projects = [project[0] for project in query.fetchall()]
    
col1, col2 = st.columns(2)

with col1:
    st.selectbox(label="What's your role?", options=[
        "Advisor", "Technical"], label_visibility="visible", placeholder="Role", key="chat_role")

with col2:
    st.selectbox(label="Project", options=projects, label_visibility="visible", key="chat_project", placeholder="Project")

st.text_input(
    label="message", label_visibility="hidden", on_change=on_input_change, key="user_input", placeholder="Question")
