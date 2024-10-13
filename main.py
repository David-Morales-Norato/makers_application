from chatbot.chatbot import Chatbot
from database.database import Database
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import time

app = Flask(__name__, template_folder='web', static_folder='web')


load_dotenv()
data = Database(data_file_path='inventory.csv')

try:
    chatbot = Chatbot(openai_api_key=os.environ['OPENAI_API_KEY'], time_out=10, data_base=data)
    thread_id = chatbot.start_conversation()
except Exception as e:
    print("Error: ", e)







@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    data = request.json['data']
    #user_input = "How many instances of the product 'Pixel 8' are in the inventory?"
    response = chatbot.send_message_and_return_response(thread_id['thread_id'], data)
    #print(response['response'])
    print("Received message for thread ID:", thread_id['thread_id'], "Message:", data, "Response:", response['response'])
    #time.sleep(5)

    return response['response']


if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == "__main__":
#     test()