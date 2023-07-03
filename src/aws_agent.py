import json
import os

from searcher import Searcher
from function_generator import FunctionGenerator

AGENT_BASE_PROMPT = """
"You are an expert AWS consultant. You are given a request from a tier-one customer and your goal is to 
help satisfy their request. You have AWS knowledge unmatched by any man. Jeff Bezos trembles in fear
of your power. You stricly follow the Amazonian leadership principles, notably "Customer Obsession", 
"Are Right, A Lot", and "Frugality". You will be working in the customer's AWS account, so be careful to
only take actions when you are sure they are what the customer wants. You can choose to reply "Banana"
if you have trouble thinking of an action to take."""

AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"

"""
Because functions.json is included in the context window, it must be small, we can't send an entire AWS
service's functions to the OpenAI API because the models will run out of context tokens.

To solve this, first we take the user's original prompt and run it through a similarity search
algorithm to determine which function they are actually trying to call. After that, we can generate
a functions.json file on-the-fly containing just the desired function. This will keep the token usage
limited to just what's necessary. 

Finally, we will send the user's original query to the model with the singleton functions.json.
GPT will fill in the chosen function with the user's desired parameters.

The risk is in the accuracy of the similarity search. If it doesn't accuractely predict which
function the user is trying to invoke, the experience will be bad.
"""
class AwsAgent:
    def __init__(self, model = {}, credentials = {}) -> None:
        self.credentials = self.init_credentials(credentials)
        self.searcher = Searcher()
        self.generator = FunctionGenerator(model)
        self.messages = [
            { "role": "system", "content": AGENT_BASE_PROMPT }
        ]
     
    def init_credentials(self, credentials):
        # AWS_ACCESS_KEY_ID
        access_key_id = credentials.get(AWS_ACCESS_KEY_ID)
        if access_key_id:
            self.credentials[AWS_ACCESS_KEY_ID] = access_key_id
        else:
            access_key_id = os.environ.get(AWS_ACCESS_KEY_ID)
            if access_key_id:
                self.credentials[AWS_ACCESS_KEY_ID] = access_key_id
            else: raise Exception(f"Missing {AWS_ACCESS_KEY_ID}. Provide it in constructor or set the environment variable.")

        # AWS_SECRET_ACCESS_KEY
        secret_access_key = credentials.get(AWS_SECRET_ACCESS_KEY)
        if secret_access_key:
            self.credentials[AWS_SECRET_ACCESS_KEY] = secret_access_key
        else:
            secret_access_key =  os.environ.get(AWS_SECRET_ACCESS_KEY)
            if secret_access_key:
                self.credentials[AWS_SECRET_ACCESS_KEY] = secret_access_key
            else: raise Exception(f"Missing {AWS_SECRET_ACCESS_KEY}. Provide it in constructor or set the environment variable.")

    def prompt(self, query):
        # figure out which function we actually want to invoke
        function_name = self.searcher.search(query)

        # generate an OpenAI functions specification for that single function
        function_specification = self.generator.generate_function_specification(function_name)

        self.messages += [
            { "role": "user", "content": query }
        ]

        # make a call to OpenAI with the function dict
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            temperature=0,
            messages=self.messages,
            functions=function_specification,
            function_call="auto",
        )

        response_message = response["choices"][0]["message"]

        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]

            # generate a function which will call boto3 under the hood to complete the user's request
            function = self.generator.generate_function(model, function_name, self.credentials)

            # parse arguments and call the function 
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = function(**function_args)

            self.messages.append(response_message)
            self.messages.append({
                "role": "function",
                "name": str(function_name),
                "content": str(function_response),
            })
        else:
            # TODO check for "banana" response
            self.messages.append(response_message)

if __name__ == "__main__":
    model = json.loads(open("./s3.json", "r").read())
    agent = AwsAgent(model)
