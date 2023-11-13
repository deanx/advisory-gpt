from langchain.document_loaders import DirectoryLoader, PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings


def load(file_name, project, username):
    print(file_name, project, username)

    loader = DirectoryLoader(
        './user_data/jsmith/' + project, glob="**/" + file_name, loader_cls=PDFPlumberLoader)

    embeddings = HuggingFaceEmbeddings()

    data = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1200, chunk_overlap=100)
    texts = text_splitter.split_documents(data)

    vectordb = Chroma.from_documents(
        texts, embeddings, persist_directory="./embeddings/" + username + "/" + project)

    print(data)
    vectordb.persist()
