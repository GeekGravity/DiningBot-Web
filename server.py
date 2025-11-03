from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from secrets import token_hex
from supabase import create_client
import os

app = FastAPI()

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
      <body style="font-family: Arial; max-width:500px; margin:60px auto;">
        <h2>Subscribe to SFU Dining Bot</h2>
        <form action="/subscribe" method="post">
          <input type="email" name="email" placeholder="Enter your email"
                 style="padding:8px; width:80%;" required>
          <button type="submit" style="padding:8px 16px; margin-left:8px;">Subscribe</button>
        </form>
        <p style="margin-top:14px;color:#555;">You will receive the daily menu every morning.</p>
      </body>
    </html>
    """


@app.post("/subscribe", response_class=HTMLResponse)
def subscribe(email: str = Form(...)):
    email = email.strip().lower()

    if not basic_valid(email):
        return "<h3>Invalid email</h3>"

    t = token_hex(16)  # 32 char

    # upsert (so user can re-subscribe)
    supabase.table("subscribers").upsert({
        "email": email,
        "token": t,
        "active": True
    }).execute()

    return f"""
    <h3>Subscription successful!</h3>
    <p>You will begin receiving daily menus.</p>
    """


@app.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(token: str):
    supabase.table("subscribers").update({"active": False}).eq("token", token).execute()

    return """
    <h3>You are unsubscribed.</h3>
    <p>You will no longer receive daily menu emails.</p>
    """
