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
import pandas as pd
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
data_sales = Database(data_file_path='sales.csv')
try:
    chatbot = Chatbot(openai_api_key=os.environ['OPENAI_API_KEY'], time_out=10, data_base=data)
    thread_id = chatbot.start_conversation()
    chatbot.send_message_and_return_response(thread_id['thread_id'], f"Use this data to answer the customer's questions.{data.data.to_string()}")
except Exception as e:
    print("Error: ", e)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    recommendations = db.Column(db.String(80), nullable=False, default='')

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


FIRST_TIME = True

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if FIRST_TIME:
        chatbot.register_user(thread_id['thread_id'], user_name=current_user.username, like = current_user.recommendations)
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    #return render_template('dashboard.html', name = data.get_columns('name'), price = data.get_columns('price'), quantity = data.get_columns('quantity'), product_type = data.get_columns('product_type'))

    # Sample Data (Replace with actual data retrieval logic)
    # Chart 1: Total Sales Over Time
    # sales_dates = ['2023-10-01', '2023-10-02', '2023-10-03', '2023-10-04', '2023-10-05']
    # sales_amounts = [1500, 2000, 1800, 2200, 2400]

    df = data_sales.data #  date_of_sale,product,price
    # Group sales by month
    df['date_of_sale'] = pd.to_datetime(df['date_of_sale'])
    df['month'] = df['date_of_sale'].dt.to_period('M')
    monthly_sales = df.groupby('month')['price'].sum().reset_index()
    sales_dates = monthly_sales['month'].astype(str).tolist()
    sales_amounts = monthly_sales['price'].tolist()

    # # Chart 2: Top Selling Products
    # top_product_names = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    # top_product_quantities = [120, 95, 80, 75, 60]
    # Get top 5 products by quantity sold
    top_products = df.groupby('product')['price'].sum().reset_index()
    top_products = top_products.sort_values(by='price', ascending=False).head(5)
    top_product_names = top_products['product'].tolist()
    top_product_quantities = top_products['price'].tolist()


    # Chart 3: Sales by Category
    #category_names = ['Electronics', 'Clothing', 'Books', 'Home & Kitchen', 'Toys']
    #category_sales = [5000, 3000, 2000, 1500, 1000]

    # Get sales by product type
    category_sales = df.groupby('product_type')['price'].sum().reset_index()
    category_sales = category_sales.sort_values(by='price', ascending=False)
    category_names = category_sales['product_type'].tolist()
    category_sales = category_sales['price'].tolist()


    return render_template(
        'dashboard.html',
        sales_dates=sales_dates,
        sales_amounts=sales_amounts,
        top_product_names=top_product_names,
        top_product_quantities=top_product_quantities,
        category_names=category_names,
        category_sales=category_sales,
        name = data.get_columns('name'),
        quantity = data.get_columns('quantity'),
    )

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

@app.route('/recomendacion', methods=['GET', 'POST'])
@login_required
def recomendacion():
    "asdasd"
    return "asdasd"
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