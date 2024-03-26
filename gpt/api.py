import openai

import os
import json

from utils import (
    calc_msg_tokens, load_apikey, create_apikey, pack_msg
)

price_dict = {
    "gpt-3.5-turbo-0613": 0.5,
    "gpt-4": 30,
    "gpt-4-32k": 60,
    "gpt-4-0125-preview": 10
}

def calculate_price():
    folder_path = "./results"
    for i, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if not filename.split(".")[-1]=="txt":
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            messages = [pack_msg(text)]
            tk = calc_msg_tokens(messages, model="gpt-4-0613")
            print(tk)
            print("single message price", price_dict["gpt-4"] * tk / 1000000)
            print("")


class DialogueConifg:
    def __init__(self, path, model_name="gpt-3.5-turbo-0125"):
        self.path = path
        self.model_name = model_name
        self.prompt = {}

    def edit_prompt(self, role, prompt, opt="add"):
        if opt=="add":
            self.prompt[role].append(prompt)
        elif opt=="replace":
            self.prompt[role] = [prompt]

    @staticmethod
    def init():
        path = input("Enter the path to save the config file: ")
        model_name = input("Enter the model name: ")
        if input("Do you want to create new api key? (y/n): ")=="y":
            pvt_path, api_path = create_apikey(input("Enter the api key: "))
        else:
            pvt_path = input("Enter the path to private key: ")
            api_path = input("Enter the path to api key: ")
        try:
            load_apikey(pvt_path, api_path)
        except Exception as e:
            raise e
        self_obj = DialogueConifg(path, model_name)
        self_obj.pvt_path = pvt_path
        self_obj.api_path = api_path
        return self_obj

    @staticmethod
    def save(self_obj):
        config_dict = {
            "path": self_obj.path,
            "model_name": self_obj.model_name,
            "prompt": self_obj.prompt,
            "api_key": {
                "pvt_path": self_obj.pvt_path,
                "api_path": self_obj.api_path,
            }
        }
        json.dump(config_dict, open(self_obj.path, "w"), indent=4)

    @staticmethod
    def load(path):
        config_dict = json.load(open(path, "r"))
        self_obj = DialogueConifg(config_dict["path"], config_dict["model_name"])
        self_obj.prompt = config_dict["prompt"]
        self_obj.pvt_path = config_dict["api_key"]["pvt_path"]
        self_obj.api_path = config_dict["api_key"]["api_path"]
        return self_obj

class OpenAIDialogue:
    def __init__(self, config_path):
        if not os.path.exists(config_path):
            config = DialogueConifg.init()
            config_path = config.path
            DialogueConifg.save(config)
        config: DialogueConifg = DialogueConifg.load(config_path)
        api_key = load_apikey(config.pvt_path, config.api_path)
        openai.api_key = api_key
        self.config = config

    def ask(self, question):
        msg = prompt2prompt(self.config.prompt)
        msg.append(pack_msg(question, "user"))
        response = openai.chat.completions.create(
            model = self.config.model_name,
            messages=msg
        )
        return response.choices[0].message.content

def prompt2prompt(prompt): # TODO now it is only for system prompt, and will be deprecated
    message = []
    for role, text in prompt.items():
        for txt in text:
            message.append(pack_msg(txt, role))
    return message


if __name__=="__main__":
    chatbot = OpenAIDialogue("config.json")
    res = chatbot.ask("What is the capital of India?")
