# Tech Guru - AI-Powered Chatbot for E-commerce

We are a team of passionate scientists and developers who have created **Tech Guru**, an AI-powered chatbot designed to bring the personalized service of a physical sales team to your online store. This application not only engages customers in real-time conversations but also provides personalized recommendations using advanced client data analysis.

Additionally, we provide a **comprehensive dashboard** for administrators to track key metrics and make informed decisions about the business.

## Contributors
- [David Najera Escobar](https://github.com/davi3004)
- [David Morales Norato](https://github.com/David-Morales-Norato)


## Features

- **AI-Powered Chatbot**:
  - Real-time customer engagement.
  - Personalized recommendations based on client data.
  - Automated responses for product features, pricing, and availability.

- **Admin Dashboard**:
  - Real-time performance analytics.
  - Revenue tracking and customer engagement metrics.
  - Insights into best-selling products and trends.

## Tech Stack

- **Backend**: Python, Flask
- **AI Integration**: Natural Language Processing (NLP) using OpenAI's GPT API
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/David-Morales-Norato/makers_application.git
    cd makers_application
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
   - Add your OpenAI API key to the environment variables:
     ```bash
     export OPENAI_API_KEY='your-openai-api-key-here'
     ```
     On Windows, use:
     ```cmd
     set OPENAI_API_KEY=your-openai-api-key-here
     ```

5. **Run the application**:
    ```bash
    python main.py
    ```

6. **Access the application**:
   - Open your browser and go to `http://127.0.0.1:5000`

## Usage

- **Customer Engagement**: Interact with the AI chatbot on your store's interface.
- **Admin Dashboard**: Monitor store performance metrics and gain insights into product sales and customer engagement.

## Project Structure

- `main.py`: Entry point to run the application.
- `app/`: Contains the Flask application logic.
- `static/`: Frontend files (HTML, CSS, JS).
- `templates/`: HTML templates for the app.
- `database.db`: SQLite database file.
- `requirements.txt`: List of dependencies.



## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
