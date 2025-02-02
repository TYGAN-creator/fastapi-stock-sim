from fastapi import FastAPI
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Initialize FastAPI
app = FastAPI()

# Google Sheets API Setup
CREDENTIALS_FILE = r"C:\Users\tecky\OneDrive\Desktop\Stock_Simulation\premium-country-449714-s4-8aaad326710a.json"  # Update with your file
SPREADSHEET_NAME = "Stock_Trading_Simulation"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME)

# Connect to Google Sheets
participants_sheet = sheet.worksheet("Participants")
trades_sheet = sheet.worksheet("Trade_Records")
leaderboard_sheet = sheet.worksheet("Leaderboard")

@app.get("/")
def home():
    return {"message": "Stock Trading Simulation API is running!"}

# API to get all participants
@app.get("/participants")
def get_participants():
    data = participants_sheet.get_all_records()
    return {"participants": data}

# API to add a trade
@app.post("/trade/")
def log_trade(user_id: int, action: str, stock: str, price: float, quantity: int):
    # Get user balance
    users = participants_sheet.get_all_records()
    df = pd.DataFrame(users)
    user_row = df[df["User ID"] == user_id].index.tolist()

    if not user_row:
        return {"error": "User ID not found!"}

    user_row = user_row[0] + 2
    current_balance = float(participants_sheet.cell(user_row, 3).value)
    total_cost = price * quantity

    if (action == "Buy" or action == "buy" ) and total_cost > current_balance:
        return {"error": "Insufficient balance!"}

    new_balance = current_balance - total_cost if (action == "Buy" or action =="buy") else current_balance + total_cost
    participants_sheet.update_cell(user_row, 3, new_balance)

    trades_sheet.append_row([user_id, action, stock, price, quantity, new_balance])

    return {"message": "Trade successful!", "new_balance": new_balance}

# API to get the leaderboard
@app.get("/leaderboard")
def get_leaderboard():
    data = leaderboard_sheet.get_all_records()
    return {"leaderboard": data}
