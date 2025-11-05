from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
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
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>DiningBot Daily</title>
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
                <h1 class="text-3xl font-semibold text-center mb-4">Thank you! 🎉</h1>
                <p class="text-center text-white/80 text-sm leading-relaxed">
                  You're now subscribed to SFU's Daily Dining Menu.
                  Tomorrow morning you'll wake up to the SFU Dining Hall menu in your inbox.
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
@app.post("/subscribe", response_class=HTMLResponse)
def subscribe(email: str = Form(...)):
    email = email.strip().lower()

    if not basic_valid(email):
        return """
        <html><body style="text-align:center; font-family:sans-serif; padding:40px;">
        <h3 style="color:red;">Invalid email address.</h3>
        <a href="/" style="color:#007BFF;">Go back</a>
        </body></html>
        """

    t = token_hex(16)

    supabase.table("subscribers").upsert({
        "email": email,
        "token": t,
        "active": True
    }).execute()

    return """
    <html><body style="text-align:center; font-family:sans-serif; padding:40px;">
    <h3 style="color:green;">Subscription successful!</h3>
    <p>You will begin receiving daily menus.</p>
    <a href="/" style="color:#007BFF;">Back to home</a>
    </body></html>
    """
