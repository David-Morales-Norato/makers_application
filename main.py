from chatbot.chatbot import Chatbot
from database.database import Database
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import time

from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

import json

app = Flask(__name__, template_folder='web', static_folder='web')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

load_dotenv()
data = Database(data_file_path='inventory.csv')

try:
    chatbot = Chatbot(openai_api_key=os.environ['OPENAI_API_KEY'], time_out=10, data_base=data)
    thread_id = chatbot.start_conversation()
except Exception as e:
    print("Error: ", e)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')




@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', name = data.get_columns('name'), price = data.get_columns('price'), quantity = data.get_columns('quantity'), product_type = data.get_columns('product_type'))

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    data = request.json['data']
    #user_input = "How many instances of the product 'Pixel 8' are in the inventory?"
    response = chatbot.send_message_and_return_response(thread_id['thread_id'], data)
    #print(response['response'])
    print("Received message for thread ID:", thread_id['thread_id'], "Message:", data, "Response:", response['response'])
    #time.sleep(5)

    return response['response']

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


#@app.route('/dashboard', methods=['GET', 'POST'])
#@login_required
#def dashboard():
#    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)





if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == "__main__":
#     test()