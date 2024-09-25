def call_openai(messages, client, model, **kwargs):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs
    )
    response_message = response.choices[0].message
    return response_message
