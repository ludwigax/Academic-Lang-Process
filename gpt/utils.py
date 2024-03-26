import os
from cryptography.fernet import Fernet

import tiktoken

def create_apikey(api_key="your_openai_api_key", pvt_path="openai.key", api_path="api_key"):
    key = Fernet.generate_key()
    with open(pvt_path, "wb") as key_file:
        key_file.write(key)

    f = Fernet(key)
    encrypted_key = f.encrypt(api_key.encode())
    with open(api_path, "wb") as key_file:
        key_file.write(encrypted_key)
    return pvt_path, api_path

def load_apikey(pvt_path="openai.key", api_path="api_key"):
    if not (os.path.exists(api_path) or os.path.exists(pvt_path)):
        raise FileNotFoundError("API key not found")
    
    with open(api_path, "rb") as key_file:
        encrypted_key = key_file.read()
    with open(pvt_path, "rb") as key_file:
        key = key_file.read()
    
    f = Fernet(key)
    api_key = f.decrypt(encrypted_key).decode()
    return api_key


def calc_msg_tokens(messages, model="gpt-3.5-turbo-0125"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125.")
        return calc_msg_tokens(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return calc_msg_tokens(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""calc_msg_tokens() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def pack_msg(text, role="user"):
    return {"role": "user", "content": text}