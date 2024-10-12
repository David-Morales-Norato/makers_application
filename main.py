from chatbot.chatbot import test
from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder='templates', static_folder='templates/assets')
chatbot = None
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def index():    
    user_message = request.form['user_message']
    print(user_message)
    return render_template('index.html')




if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == "__main__":
#     test()