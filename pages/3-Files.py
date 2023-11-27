import streamlit as st
import streamlit_authenticator as stauth

import yaml

import os.path
import pathlib

import sqlite3

import os

import datetime

from yaml.loader import SafeLoader
from data_loader import load_file, reload_embeddings
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
    query = cursor.execute(
        "select id, project from projects where username='" + username + "'")
    projects = [row[1] for row in query.fetchall()]


def delete_file(file_id, file_name, project):
    with sqlite3.connect("projects.db") as conn:
        parent_path = pathlib.Path(__file__).parent.parent.resolve()
        save_path = os.path.join(parent_path, "user_data/" + username, project)

        complete_name = os.path.join(save_path, file_name)
        os.remove(complete_name)

        reload_embeddings(project, username)

        cursor = conn.cursor()

        cursor.execute("delete from files where id='" + str(file_id) + "'")

        st.toast("Deleted file " + file_name)


with st.container():
    project = st.selectbox("Project:", options=projects, key="file_project", )

    st.divider()

    with sqlite3.connect("projects.db") as connection:
        cursor = connection.cursor()
        query = cursor.execute("select id from projects where project='" +
                               st.session_state.file_project + "'")

        response = query.fetchone()
        project_id = response[0]

        files_query = cursor.execute("select * from files where project_id=" +
                                     str(project_id))

        files = files_query.fetchall()

        for id, project_id, date_add, file_name in files:
            col1, col2 = st.columns(2)
            col1.text(file_name)
            col2.button("delete", key=id, on_click=delete_file,
                        args=[id, file_name, st.session_state.file_project])
            st.divider()

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
        load_file(uploaded_file.name, st.session_state.file_project, username)

        with sqlite3.connect("projects.db") as connection:
            cursor = connection.cursor()
            query = cursor.execute("insert into files (project_id, date_add, file_name) values(" +
                                   project_id + ",'" + str(datetime.date.today()) + "', '" + uploaded_file.name + "');")

        st.toast("File uploaded")
