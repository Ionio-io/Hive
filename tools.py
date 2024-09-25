from clients import ppxl_client


def perplexity_search(query: str) -> str:
    system_message = """
    You are a helpful assistant that can answer questions.
    You are an expert at searching the internet for information.
    You have to search for what the user tells you in detail.
    
    Format your responses in a way that is easy to understand.
    
    Your responses are to be detailed, go very wide, and gather as much information as possible.
    If you think there are interesting things the user can learn more about, you can mention them.
    """
    
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]
        

    response = ppxl_client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
        temperature=0.1
    )
    
    response_text = response.choices[0].message.content

    return response_text
