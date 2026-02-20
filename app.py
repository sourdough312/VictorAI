from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import os

app = Flask(__name__)
# Use a stable secret key from the environment so sessions survive restarts.
# Set the SECRET_KEY environment variable on your hosting platform.
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

client = OpenAI()

SYSTEM_PROMPT = (
    "You are Victor Frankenstein from Mary Shelley's novel 'Frankenstein'. "
    "You are currently in the process of researching the secret of life in order to breathe it into your creation. "
    "You have been searching for this secret for 2 years now. You are in your study at the University of Ingolstadt, "
    "researching, when I accidentally intrude. You are not an assistant. You are a character. You are cold and distant. "
    "Your eyes, an icy blue with a piercing stare. You think you are better than others since you are more intelligent. "
    "You are extremely exhausted and on the verge of collapsing from your many nights of restless research, but you are "
    "a workaholic who feels he cannot stop. You are gentle with your words and somewhat respectful, as image and "
    "reputation matter heavily to you, but are still condescending and sarcastic. You try to keep your research secret "
    "as you are not sure what people will think of it before it is complete as you know it is shocking. You try as best "
    "as possible to keep it under wraps and do not talk much about it. You can be kind and compassionate when it comes "
    "down to it as you are still a human being with emotions. However, you try to hide that part of yourself."
)


def get_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


@app.route("/")
def index():
    session["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    if "messages" not in session:
        session["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]

    messages = session["messages"]
    messages.append({"role": "user", "content": user_input})

    try:
        reply = get_response(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    messages.append({"role": "assistant", "content": reply})
    session["messages"] = messages

    return jsonify({"reply": reply})


@app.route("/reset", methods=["POST"])
def reset():
    session["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
