import sqlite3

from yaml.loader import SafeLoader
import yaml
import streamlit_authenticator as stauth
import streamlit as st
import warnings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Bedrock

from langchain.embeddings import HuggingFaceEmbeddings

from langchain.chains.question_answering import load_qa_chain
from langchain import PromptTemplate


from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import SQLChatMessageHistory

import docs
import prompt_template


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


def generate_response(message, project, role="Advisor"):

    llm = get_llm()

    final_docs = docs.docs(project, message, embeddings, role)

    pt = prompt_template.generate_prompt_template(project, role)

    prompt = PromptTemplate(
        template=pt, input_variables=[
            "chat_history", "context", "question"]
    )

    message_history = SQLChatMessageHistory(session_id="session_id",
                                            connection_string="sqlite:///history/" + project + ".db")

    memory = ConversationBufferMemory(llm=llm, return_messages=True,
                                      memory_key="chat_history", input_key='question', chat_memory=message_history)

    chain = load_qa_chain(llm, chain_type="stuff",
                          memory=memory, prompt=prompt)

    print("here it goes!", memory.to_json, " and how it was!")

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
    response = generate_response(
        st.session_state.user_input, project, chat_role)

    st.session_state.messages.append({"role": "user", "content": input})
    st.session_state.messages.append(
        {"role": "assistant", "content": response})


with sqlite3.connect("projects.db") as connection:
    cursor = connection.cursor()
    query = cursor.execute(
        "select project from projects where username='" + username + "'")
    projects = [project[0] for project in query.fetchall()]

col1, col2 = st.columns(2)

with col1:
    st.selectbox(label="What's your role?", options=[
        "Advisor", "Technical"], label_visibility="visible", placeholder="Role", key="chat_role")

with col2:
    st.selectbox(label="Project", options=projects,
                 label_visibility="visible", key="chat_project", placeholder="Project")

st.text_input(
    label="message", label_visibility="hidden", on_change=on_input_change, key="user_input", placeholder="Question")
