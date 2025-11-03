from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from secrets import token_hex
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
BASE_URL = os.environ.get("BASE_URL", "https://sfudiningbot.onrender.com")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def basic_valid(email: str) -> bool:
    return "@" in email and "." in email


@app.get("/", response_class=HTMLResponse)
def subscribe_page():
    return """
    <html>
      <head>
        <title>Subscribe to SFU Dining Bot</title>
        <style>
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            height: 100vh;
            background-image: url('/static/backgoun.png'); /* 🔁 Replace with your background */
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            display: flex;
            justify-content: center;
            align-items: center;
          }

          .overlay {
            background-color: rgba(255, 255, 255, 0.85); /* Dark red overlay */
            border-radius: 12px;
            padding: 40px;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            text-align: center;
            color: #8B0000;
          }

          h2 {
            margin-bottom: 20px;
            color: #8B0000;
          }

          input[type="email"] {
            width: 100%;
            padding: 12px;
            border-radius: 6px;
            border: none;
            margin-bottom: 16px;
            font-size: 16px;
            background-color: #fff;
            color: #000;
          }

          input::placeholder {
            color: #777;
          }

          button {
            padding: 12px 24px;
            background-color: #ffffff;
            color: #8B0000;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.2s ease, color 0.2s ease;
          }

          button:hover {
            background-color: #f2f2f2;
            color: #660000;
          }

          p {
            color: #8B0000;
            margin-top: 20px;
            font-size: 14px;
          }
        </style>
      </head>
      <body>
        <div class="overlay">
          <h2>Subscribe to SFU Dining Bot</h2>
          <form action="/subscribe" method="post">
            <input type="email" name="email" placeholder="Enter your email" required>
            <button type="submit">Subscribe</button>
          </form>
          <p>You will receive the daily menu every morning.</p>
        </div>
      </body>
    </html>
    """



@app.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(token: str):
    supabase.table("subscribers").update({"active": False}).eq("token", token).execute()

    return """
    <html><body style="text-align:center; font-family:sans-serif; padding:40px;">
    <h3>You are unsubscribed.</h3>
    <p>You will no longer receive daily menu emails.</p>
    <a href="/" style="color:#007BFF;">Resubscribe</a>
    </body></html>
    """
