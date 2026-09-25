import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Token ekhon environment variable theke asbe, code-e hardcode kora nei
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Group invite link o environment variable theke, na thakle default value use hobe
GROUP_LINK = os.environ.get("GROUP_LINK", "https://t.me/+wu0s4ciR9AhhMTk1")


# ---------------------------------------------------------------------------
# Render-er Free Web Service ekta open port asha kore, nahole "no open port
# detected" bole deploy fail kore dey. Bot nijei kono port lage na (polling
# mode), tai ekta chotto dummy HTTP server chalu kore rakhchi shudhu
# health-check pass korar jonno.
# ---------------------------------------------------------------------------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running.")

    def log_message(self, format, *args):
        # Access log terminal-e print hobe na, shudhu bot-er nijer log dekha jabe
        pass


def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Health-check server running on port {port}")
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name
    username = f"@{user.username}" if user.username else "No Username"
    user_id = user.id

    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    print(f"[{current_time}] 📥 New User: {user_name} | {username} | ID: {user_id}")

    # Note: Render-er free instance-e filesystem ephemeral, tai restart hole
    # ei file muche jete pare. Persistent storage lagle Render Disk add korte hobe.
    with open("users.txt", "a", encoding="utf-8") as f:
        f.write(f"Time: [{current_time}] | Name: {user_name} | Username: {username} | ID: {user_id}\n")

    message_text = (
        f"Hello {user_name}! 👋 Welcome.\n\n"
        f"To join our active engagement group, please click the link below:\n{GROUP_LINK}\n\n"
        f"See you inside!"
    )

    await update.message.reply_text(message_text)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable set kora nei! Render dashboard-e set korun.")

    # Health-check server alada thread-e background-e chalu
    threading.Thread(target=run_health_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot is running in English mode and saving users...")
    app.run_polling()


if __name__ == '__main__':
    main()
