import streamlit as st
import streamlit_authenticator as stauth

import yaml

import os.path
import pathlib
import shutil

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

def delete_project(project):
    
    
    with sqlite3.connect("projects.db") as conn:
        cursor = conn.cursor()
        cursor.execute("delete from projects where project='" + project + "'")   
        parent_path = pathlib.Path(__file__).parent.parent.resolve()
        shutil.rmtree(os.path.join(parent_path, "embeddings", username, project))
        shutil.rmtree(os.path.join(parent_path, "user_data", username, project))
        st.toast("Deleted project " +  project)
for project  in projects:
    col1, col2 = st.columns(2)
    col1.text(project)
    col2.button("delete", key=project, on_click=delete_project, args=[project])
    st.divider()

def add_project():
    new_project = st.session_state.get("new_project")
    if(len(new_project) < 5):
        st.toast("Invalid project name")
        return
    with sqlite3.connect("projects.db") as connection:
        cursor = connection.cursor()
        cursor.execute("insert into projects (username, project) values ('"+username+"','"+new_project+"');")
        os.mkdir("./embeddings/" + username + "/" + new_project, 0o777)
        os.mkdir("./user_data/" + username + "/" + new_project, 0o777)
        st.toast("Project added")
        
        
st.text_input(label="new project", label_visibility="hidden", placeholder="New project name", key="new_project", on_change=add_project)
