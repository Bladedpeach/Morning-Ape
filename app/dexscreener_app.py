import os
import sys
import requests
from telegram import Bot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLabel


# Function to fetch token data from Dexscreener API
def fetch_token_data():
    url = "https://api.dexscreener.com/latest/dex/tokens"
    try:
        response = requests.get(url, timeout=10)  # Add a 10-second timeout
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch token data: {str(e)}")


# Function to analyze token data
def analyze_token_data(token_data):
    analyzed_data = []
    for token in token_data["pairs"][:5]:  # Limit to top 5 tokens for simplicity
        price_usd = float(token["priceUsd"]) if "priceUsd" in token else 0
        volume_h24 = float(token["volume"]["h24"]) if "volume" in token and "h24" in token["volume"] else 0
        analyzed_data.append({
            "name": token["baseToken"]["name"],
            "ca": token["baseToken"]["address"],
            "description": f"Price: {price_usd:.2f} USD, Volume: {volume_h24:.2f}"
        })
    return analyzed_data


# Function to send Telegram messages
def send_telegram_message(token_name, ca, description):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise Exception("Telegram bot token or chat ID not found in environment variables")

    try:
        bot = Bot(token=bot_token)
        message = f"Token: {token_name}\nCA: {ca}\nDescription: {description}"
        bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        raise Exception(f"Failed to send Telegram message: {str(e)}")


# PyQt5 GUI Application
class DexscreenerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Dexscreener Analyzer")
        self.setGeometry(100, 100, 600, 400)

        self.text_box = QTextEdit(self)
        self.text_box.setReadOnly(True)
        self.text_box.setGeometry(20, 20, 560, 300)

        self.status_label = QLabel(self)
        self.status_label.setGeometry(20, 320, 560, 20)
        self.status_label.setText("Ready")

        self.btn_fetch = QPushButton("Fetch and Analyze", self)
        self.btn_fetch.setGeometry(20, 340, 560, 40)
        self.btn_fetch.clicked.connect(self.fetch_and_analyze)

    def fetch_and_analyze(self):
        try:
            self.status_label.setText("Fetching token data...")
            token_data = fetch_token_data()
            self.status_label.setText("Analyzing token data...")
            analyzed_data = analyze_token_data(token_data)
            self.text_box.setText(str(analyzed_data))
            self.status_label.setText("Sending Telegram messages...")
            for token in analyzed_data:
                send_telegram_message(token["name"], token["ca"], token["description"])
            self.status_label.setText("Done")
        except Exception as e:
            self.status_label.setText("Error occurred")
            self.text_box.setText(f"Error: {str(e)}")


# Main entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DexscreenerApp()
    window.show()
    sys.exit(app.exec_())