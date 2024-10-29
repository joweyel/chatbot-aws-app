from flask import (  # pylint: disable=W0611
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from langchain_core.messages import HumanMessage
from website.utils.utils import parseMD

from . import db, init_chatbot
from .models import Chat, Message

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
def home():
    print("HOME")
    chatbot = current_app.config.get("chat_bot", None)
    if chatbot is None:
        flash("Chatbot is not initialized!", category="error")
        return render_template("home.html", chat=None)

    chat_id = current_app.config["llm_config"]["configurable"]["thread_id"]

    if request.method == "POST":
        user_msg = request.form.get("user_message")
        if not isinstance(user_msg, str):
            flash("Invalid input provided!", category="error")
        elif len(user_msg) < 1:
            flash("Empty message!", category="error")
        elif len(user_msg) > 4000:
            flash("Input is too long!", category="error")
        else:
            human_msg = [HumanMessage(user_msg)]
            output = chatbot.invoke(
                {"messages": human_msg}, current_app.config["llm_config"]
            )
            ai_msg = output["messages"][-1].content
            print(">> User:", user_msg, "AI:", ai_msg)  # Debugging output

            chat = Chat.query.filter_by(id=chat_id).first()
            if chat is None:
                chat = Chat(id=chat_id)
                db.session.add(chat)
                db.session.commit()

            message_user = Message(role="user", content=user_msg, chat=chat)
            db.session.add(message_user)

            message_ai = Message(role="assistant", content=ai_msg, chat=chat)
            db.session.add(message_ai)
            db.session.commit()

            return jsonify(
                usr_msg=parseMD(message_user.content),
                ai_msg=parseMD(message_ai.content),
            )

    chat = Chat.query.filter_by(id=chat_id).first()
    if chat and chat.messages:
        for msg in chat.messages:
            msg.content = parseMD(msg.content)
    return render_template("home.html", chat=chat)


@views.route("/reset_chat", methods=["POST"])
def reset_chat():
    print("reset_chat")
    # Reset the chatbot (start with fresh memory)
    init_chatbot(current_app)
    # Clear the sqlite database with saved chats and messages
    Message.query.delete()
    Chat.query.delete()
    db.session.commit()
    return jsonify(status="success", message="Chat cleared!")
