import pathlib
import os.path
from langchain.vectorstores import Chroma


def docs(project, message, embeddings, role="Advisor"):
    if role == "Advisor":
        project_docs = list(get_project_answer(
            message, project, embeddings, 4))
        methodology_docs = list(get_methodology_answer(message, embeddings, 4))
        tech_docs = list(get_technical_answer(message, embeddings, 2))

    else:
        project_docs = list(get_project_answer(
            message, project, embeddings, 4))
        methodology_docs = list(get_methodology_answer(message, embeddings, 4))
        tech_docs = list(get_technical_answer(message, embeddings, 2))
    return project_docs + tech_docs + methodology_docs


def get_methodology_answer(query, embeddings, weight=4):
    parent_path = pathlib.Path(__file__).parent.resolve()
    user_path = os.path.join(parent_path, "embedding_methodology")
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=user_path
    )
    return vectordb.similarity_search(query, k=weight)


def get_project_answer(query, project, embeddings, weight=4):
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory="/Users/alex/dev/deanx/ia/langchain-pdf/pdf1/bedrock_embeddings"
    )
    return vectordb.similarity_search(query, k=weight)


def get_technical_answer(query, embeddings, weight=2):
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory="/Users/alex/dev/deanx/ia/langchain-pdf/pdf1/stored"
    )
    return vectordb.similarity_search(query, k=weight)
