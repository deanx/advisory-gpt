def generate_prompt_template(project, role="Advisor"):

    if role == "Advisor":
        prompt_template = """Use ONLY the following pieces of context to answer the question at the end. 
        If you cannot find the answer in the following context, just say that you don't know, don't try to make up an answer.
        {context}
        
        {chat_history}
        
        Assuming your are a Strategic Advisor, answer the following question:
        Question: {question}
        """

    else:
        prompt_template = """Use ONLY the following pieces of context to answer the question at the end. 
            If you cannot find the answer in the following context, just say that you don't know, don't try to make up an answer.
            {context}
            
            {chat_history}
            
            Assuming your are a Software Implementation Architect, answer the following question:
            Question: {question}
            """

    return prompt_template
