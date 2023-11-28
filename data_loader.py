import pathlib
import shutil
import os
from langchain.document_loaders import DirectoryLoader, PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings


def load_file(file_name, project, username):

    loader = DirectoryLoader(
        './user_data/' + username + '/' + project, glob="**/" + file_name, loader_cls=PDFPlumberLoader)

    embeddings = HuggingFaceEmbeddings()

    data = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1200, chunk_overlap=100)
    texts = text_splitter.split_documents(data)

    vectordb = Chroma.from_documents(
        texts, embeddings, persist_directory="./embeddings/" + username + "/" + project)

    vectordb.persist()


def load_directory(directory, project, username):
    files = [f for f in pathlib.Path(directory).iterdir() if f.is_file()]
    for f in files:
        load_file(f.name, project, username)


def reload_embeddings(project, username):
    parent_path = pathlib.Path(__file__).parent.resolve()
    em_path = os.path.join(
        parent_path, "embeddings", username, project)

    shutil.rmtree(em_path)

    files_path = os.path.join(
        parent_path, "user_data", username, project)

    load_directory(files_path, project, username)
