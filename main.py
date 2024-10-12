from chatbot.chatbot import test
from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder='web', static_folder='web')
chatbot = None
@app.route('/')
def index():
    return render_template('index.html')





if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == "__main__":
#     test()