from clients import ppxl_client


def perplexity_search(query: str):
    system_message = """
    You are a helpful assistant that can answer questions. Do not use markdown. 
    Never return the names of the websites or sources, you can mention the brands and products that the user is looking for. 
    You can mention the official websites of the brands and products that the user is looking for, but never anything unofficial. 
    
    IMPORTANT RULE: RETURN ONE PARAGRAPH OF 50 WORDS MAX. NOT MORE THAN THAT, BE VERY CONCISE. 
    Never send markdown, only plain text. You can send list using new lines and stuff, but no markdown, or html, or any formatting. 
    YOU MUST NEVER USE MARKDOWN, AND ALWAYS REPLY WITHIN 200 WORDS, BE EXTREMELY SHORT. Just plain text.
    
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
