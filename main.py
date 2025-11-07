import os
from secrets import token_hex
from dotenv import load_dotenv

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from pydantic import EmailStr, ValidationError, BaseModel
from supabase import create_client


# FastAPI setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


# Supabase setup
load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Email validation
class EmailModel(BaseModel):
    email: EmailStr

def is_valid_email(email: str) -> bool:
    try:
        EmailModel(email=email)
        return True
    except ValidationError:
        return False


# Routes
@app.get("/", response_class=HTMLResponse)
def subscribe_page():
    return """
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>DiningBot Daily</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        html,body{height:100%; background-color: #000;}
        .glass {
          background: rgba(0,0,0,0.35);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255,255,255,0.15);
          box-shadow: 0 24px 48px rgba(0,0,0,0.4);
        }
        .hero-bg {
          background-image: url('/static/dining_hall.jpg');
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          min-height: 100%;
          background-color: #000; /* fallback color */
        }
        .fade {
          transition: opacity .4s ease;
        }
      </style>
    </head>
    <body class="hero-bg relative min-h-screen w-full flex items-center justify-center font-[system-ui,Inter,-apple-system,BlinkMacSystemFont] text-white">
      <div class="absolute inset-0 bg-black/45"></div>

      <div id="card" class="glass relative w-[90%] max-w-sm rounded-3xl p-8 transition-transform duration-200 hover:scale-[1.02] z-10">
        
        <!-- CONTENT WRAPPER (we will replace this on success) -->
        <div id="cardContent" class="fade opacity-100">
          <h1 class="text-3xl font-semibold text-center mb-3">SFU Daily Menu</h1>
          <p class="text-center text-sm text-white/80 mb-6">
            Wake up to the menu. Every morning. In your email.
          </p>

          <form id="subForm" class="flex flex-col space-y-3">
            <input
              type="email"
              name="email"
              required
              placeholder="you@email.com"
              class="rounded-xl bg-white/10 border border-white/20 px-4 py-3 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-300/30"
            />
            <button
              type="submit"
              class="bg-white/90 text-black rounded-xl py-3 text-sm font-medium hover:bg-white transition"
            >
              Subscribe
            </button>
          </form>
        </div>
        <!-- END WRAPPER -->

      </div>

      <script>
        const form = document.getElementById("subForm");
        const cardContent = document.getElementById("cardContent");

        form.addEventListener("submit", async (e) => {
          e.preventDefault();
          const formData = new FormData(form);
          const email = formData.get("email");

          // fade out
          cardContent.style.opacity = 0;

          const res = await fetch("/subscribe", {
            method: "POST",
            body: new URLSearchParams({ email })
          });

          if (res.ok) {
            setTimeout(() => {
              cardContent.innerHTML = `
                <h1 class="text-3xl font-semibold text-center mb-4">Thank you</h1>
                <p class="text-center text-white/80 text-sm leading-relaxed">
                  You're now subscribed to SFU's Daily Dining Menu.
                  Tomorrow morning you'll wake up to the Dining Hall menu in your inbox.
                </p>
              `;
              // fade back in
              cardContent.style.opacity = 1;
            }, 400); // match transition timing
          } else {
            alert("Something went wrong. Try again.");
            cardContent.style.opacity = 1;
          }
        });
      </script>

    </body>
  </html>
    """


from typing import Optional
from fastapi.responses import HTMLResponse

@app.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe_confirm(token: Optional[str] = None):
    if not token:
        # Token missing → show same UI but with error message
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Invalid Unsubscribe Link</title>
          <script src="https://cdn.tailwindcss.com"></script>
          <style>
            html,body{{height:100%;}}
            .glass {{
              background: rgba(0,0,0,0.35);
              backdrop-filter: blur(20px);
              -webkit-backdrop-filter: blur(20px);
              border: 1px solid rgba(255,255,255,0.15);
              box-shadow: 0 24px 48px rgba(0,0,0,0.4);
            }}
            .hero-bg {{
              background-image: url('/static/dining_hall.jpg');
              background-size: cover;
              background-position: center;
              background-repeat: no-repeat;
              min-height: 100%;
              background-color: #000; /* fallback color */
            }}
          </style>
        </head>
        <body class="hero-bg relative min-h-screen w-full flex items-center justify-center font-[system-ui,Inter,-apple-system,BlinkMacSystemFont] text-white">
          <div class="absolute inset-0 bg-black/45"></div>
          <div class="glass relative w-[90%] max-w-sm rounded-3xl p-8 z-10">
            <h1 class="text-3xl font-semibold text-center mb-6">Invalid Link</h1>
            <p class="text-center text-white/80 text-sm mb-6">
              The unsubscribe link is missing or invalid. Please check your email for the correct link.
            </p>
            <p class="text-center text-sm mt-6">
              <a href="/" class="text-white/60 underline">Back to homepage</a>
            </p>
          </div>
        </body>
        </html>
        """

    # Token exists → show normal unsubscribe form
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Unsubscribe</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        html,body{{height:100%;}}
        .glass {{
          background: rgba(0,0,0,0.35);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255,255,255,0.15);
          box-shadow: 0 24px 48px rgba(0,0,0,0.4);
        }}
        .hero-bg {{
          background-image: url('/static/dining_hall.jpg');
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          min-height: 100%;
          background-color: #000; /* fallback color */
        }}
      </style>
    </head>
    <body class="hero-bg relative min-h-screen w-full flex items-center justify-center font-[system-ui,Inter,-apple-system,BlinkMacSystemFont] text-white">
      <div class="absolute inset-0 bg-black/45"></div>
      <div class="glass relative w-[90%] max-w-sm rounded-3xl p-8 z-10">
        <h1 class="text-3xl font-semibold text-center mb-6">Unsubscribe?</h1>
        <p class="text-center text-white/80 text-sm mb-6">
          Do you want to stop receiving SFU's daily menu emails?
        </p>
        <form action="/unsubscribe_confirm" method="post" class="flex flex-col items-center">
          <input type="hidden" name="token" value="{token}">
          <button type="submit" class="bg-white/90 text-black rounded-xl px-6 py-3 text-sm font-medium hover:bg-white transition">
            Yes, unsubscribe me
          </button>
        </form>
        <p class="text-center text-sm mt-6">
          <a href="/" class="text-white/60 underline">Cancel</a>
        </p>
      </div>
    </body>
    </html>
    """

@app.post("/unsubscribe_confirm", response_class=HTMLResponse)
def unsubscribe_do(token: str = Form(...)):
    supabase.table("subscribers").update({"active": False}).eq("token", token).execute()
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Unsubscribed</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        html,body{height:100%;}
        .glass {
          background: rgba(0,0,0,0.35);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255,255,255,0.15);
          box-shadow: 0 24px 48px rgba(0,0,0,0.4);
        }
        .hero-bg {
          background-image: url('/static/dining_hall.jpg');
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          min-height: 100%;
          background-color: #000; /* fallback color */
        }
      </style>
    </head>
    <body class="hero-bg relative min-h-screen w-full flex items-center justify-center font-[system-ui,Inter,-apple-system,BlinkMacSystemFont] text-white">
      <div class="absolute inset-0 bg-black/45"></div>
      <div class="glass relative w-[90%] max-w-sm rounded-3xl p-8 z-10">
        <h1 class="text-3xl font-semibold text-center mb-6">You're unsubscribed</h1>
        <p class="text-center text-white/80 text-sm leading-relaxed mb-6">
          You will no longer receive daily menus.
        </p>
        <p class="text-center text-sm">
          <a href="/" class="text-white/60 underline">Resubscribe</a>
        </p>
      </div>
    </body>
    </html>
    """

@app.post("/subscribe")
def subscribe(email: str = Form(...)):
    email = email.strip().lower()

    if not is_valid_email(email):
        return JSONResponse({"ok": False, "error": "invalid_email"}, status_code=400)

    t = token_hex(16)

    supabase.table("subscribers").upsert({
        "email": email,
        "token": t,
        "active": True
    }).execute()

    return {"ok": True}
