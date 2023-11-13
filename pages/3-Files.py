import streamlit as st
import streamlit_authenticator as stauth

import yaml

import os.path
import pathlib

import sqlite3

from yaml.loader import SafeLoader
from data_loader import load
from contextlib import closing

with open("./config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

if "authentication_status" not in st.session_state or st.session_state["authentication_status"] == None:
    st.session_state["authentication_status"] = None
    st.info('Please enter your username and password')

name, authentication_status, username = authenticator.login('Login', 'main')


with sqlite3.connect("projects.db") as connection:
    cursor = connection.cursor()
    query = cursor.execute("select project from projects where username='" + username + "'")
    projects = [row[0] for row in query.fetchall()]
  
    
with st.container():
    project = st.selectbox("Project:", options=projects, key="file_project")
    uploaded_files = st.file_uploader(
        "Choose a PDF file:", accept_multiple_files=True, type=["pdf"])
    for uploaded_file in uploaded_files:
        project = st.session_state.file_project
        bytes_data = uploaded_file.getvalue()
        parent_path = pathlib.Path(__file__).parent.parent.resolve()
        save_path = os.path.join(parent_path, "user_data/" + username, project)
        complete_name = os.path.join(save_path, uploaded_file.name)
        
        destination_file = open(complete_name, "wb")
        destination_file.write(bytes_data)
        destination_file.close()
        load(uploaded_file.name, st.session_state.file_project, username)
        st.info("File uploaded")


