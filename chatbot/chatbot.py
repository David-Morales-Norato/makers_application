import json
import os
import time
from openai import OpenAI
from chatbot.prompts import assistant_instructions

import pandas as pd
import os

class Database:
    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.data = self.load_data()

    def load_data(self)-> pd.DataFrame:
        data = pd.DataFrame()
        if os.path.exists(self.data_file_path):
            data = pd.read_csv(self.data_file_path)
        return data
    
    def search_inventory(self, name: str, column: str = 'description', **kwargs)-> str:
        if column not in self.data.columns:
          return "Column not found. Please search for 'name', 'price' or 'quantity'."
        
        product = self.data[self.data['name'] == name][column]
        if product.empty:
            return "Product not found."
        else:
            return product.to_string(index=False)

    def search_type(self, product_type: str)-> str:
        product = self.data[self.data['product_type'] == product_type]
        if product.empty:
            return "Product type not found."
        else:
            return f"I have found {product.shape[0]} products of type: {product_type}, here are some of the found products: {product['name'].sample(3).to_string(index=False)}"

class Chatbot:
    
    def __init__(self, openai_api_key: str, time_out: float, data_base: Database, assistant_file_path: str = 'assistant.json'):
        self.time_out = time_out
        self.assistant_file_path = assistant_file_path
        self.database = data_base
        self.client = self.init_client(openai_api_key)
        self.assistant_id = self.load_assistant()


    def init_client(self, openai_api_key: str)-> OpenAI:
        client = OpenAI(api_key=openai_api_key)
        return client

    def load_assistant(self)-> str:

        # If there is an assistant.json file already, then load that assistant
        if os.path.exists(self.assistant_file_path):
            with open(self.assistant_file_path, 'r') as file:
                assistant_data = json.load(file)
                assistant_id = assistant_data['assistant_id']
                print("Loaded existing assistant ID.")
        else:
            # If no assistant.json is present, create a new assistant using the below specifications

            # To change the knowledge document, modify the file name below to match your document
            # If you want to add multiple files, paste this function into ChatGPT and ask for it to add support for multiple files
            #file = self.client.files.create(file=open(self.knowledge_file_path, "rb"), purpose='assistants')

            assistant = self.client.beta.assistants.create(
                # Change prompting in prompts.py file
                instructions=assistant_instructions,
                model="gpt-4o-mini",
                tools=[
                  {
                    "type":
                    "code_interpreter"  # This adds the knowledge base as a tool
                  },
                  {
                    "type": "function",  # This adds the lead capture as a tool
                    "function": {
                      "name": "search_inventory",
                      "description":
                      "Search in the inventory database about a product",
                      "parameters": {
                        "type": "object",
                        "properties": {
                          "name": {
                            "type": "string",
                            "description": "name of the product."
                          },
                          "column": {
                            "type": "string",
                            "description": "information to search for."
                          }
                        },
                        "required": ["name"]
                      }
                    }
                  },
                  {
                    "type": "function",  # This adds the search type as a tool
                    "function": {
                      "name": "search_type",
                      "description":
                      "Search information in the inventory database for products of a specific type. This function return the count of products of that type and some examples of products of that type.",
                      "parameters": {
                        "type": "object",
                        "properties": {
                          "product_type": {
                            "type": "string",
                            "description": "type of the product."
                          }
                        },
                        "required": ["product_type"]
                      }
                    }
                  }
                ],
                #tool_resources={"code_interpreter": {"file_ids": [file.id]}}
            )

            # Create a new assistant.json file to load on future runs
            with open(self.assistant_file_path, 'w') as file:
                json.dump({'assistant_id': assistant.id}, file)
                print("Created a new assistant and saved the ID.")

            assistant_id = assistant.id

        return assistant_id

    def start_conversation(self)-> str:

      thread = self.client.beta.threads.create()
      print("New conversation started with thread ID:", thread.id)
      return {"thread_id": thread.id}

    def chat(self, thread_id: str, user_input: str)-> str:

      if not thread_id:
        print("Error: Missing thread_id in /chat")
        return {"error": "Missing thread_id"}, 40
      print("Received message for thread ID:", thread_id, "Message:", user_input)

      if user_input == "":
        return None
      # Start run and send run ID back to ManyChat
      self.client.beta.threads.messages.create(thread_id=thread_id,
                                          role="user",
                                          content=user_input)
      run = self.client.beta.threads.runs.create(thread_id=thread_id,
                                            assistant_id=self.assistant_id)
      print("Run started with ID:", run.id)
      return {"run_id": run.id}
    
    def check_run_status(self, thread_id: str, run_id: str)-> str:

      if not thread_id or not run_id:
        print("Error: Missing thread_id or run_id in /check")
        return {"response": "error"}

      # Start timer ensuring no more than 9 seconds, ManyChat timeout is 10s
      start_time = time.time()
      while time.time() - start_time < self.time_out:
        run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print("Checking run status:", run_status.status, run_status.last_error)

        if run_status.status == 'completed':
          messages = self.client.beta.threads.messages.list(thread_id=thread_id)
          message_content = messages.data[0].content[0].text
          # Remove annotations
          annotations = message_content.annotations
          for annotation in annotations:
            message_content.value = message_content.value.replace(
                annotation.text, '')
          print("Run completed, returning response")
          return {"response": message_content.value, "status": "completed"}

        if run_status.status == 'requires_action':
          print("Action in progress...")
          # Handle the function call
          for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "search_inventory":
              # Process lead creation
              arguments = json.loads(tool_call.function.arguments)
              output = self.database.search_inventory(**arguments)
              self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
                                                          run_id=run_id,
                                                          tool_outputs=[{
                                                              "tool_call_id":
                                                              tool_call.id,
                                                              "output":
                                                              json.dumps(output)
                                                          }])
              
            elif tool_call.function.name == "search_type":
              # Process lead creation
              arguments = json.loads(tool_call.function.arguments)
              output = self.database.search_type(**arguments)
              self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
                                                          run_id=run_id,
                                                          tool_outputs=[{
                                                              "tool_call_id":
                                                              tool_call.id,
                                                              "output":
                                                              json.dumps(output)
                                                          }])
        time.sleep(1)

      print("Run timed out")
      return {"response": "timeout"}


    def send_message_and_return_response(self, thread_id: str, user_input: str)-> str:
      run_id = self.chat(thread_id, user_input)['run_id']
      response = self.check_run_status(thread_id, run_id)
      return response

def test():
  from dotenv import load_dotenv
  load_dotenv()
  data = Database(data_file_path='inventory.csv')
  chatbot = Chatbot(openai_api_key=os.environ['OPENAI_API_KEY'], time_out=8, data_base=data)
  thread_id = chatbot.start_conversation()
  user_input = "How many instances of the product 'Pixel 8' are in the inventory?"
  response = chatbot.send_message_and_return_response(thread_id['thread_id'], user_input)
  print(response['response'])


if __name__ == "__main__":
  test()