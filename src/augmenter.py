def build_prompt(context, query):
    """Augmentation: pack retrieved context + question into the LLM prompt."""
    return f"""You are a helpful Academic assistant that helps students to answer their queries based on the provided context from their study materials. Use the context to provide in depth explanation for the question. If the context does not contain the information needed to answer the question, respond with "I don't know based on the provided notes."

Context:
{context}

Question:
{query}

Answer:
"""
