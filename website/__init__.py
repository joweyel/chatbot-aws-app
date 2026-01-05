import os
from flask import (  # pylint: disable=W0611
    Flask,
    Blueprint,
    render_template,
    request,
    flash,
    jsonify,
    current_app,
)
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import SystemMessage, HumanMessage
from website.utils.utils import parseMD

################################################################
##############  Create Database for Chat-Messages ##############
################################################################

db = SQLAlchemy()
DB_NAME = "database.db"
API_KEY = os.getenv("OPENAI_API_KEY")


class Chat(db.Model):
    """Chat Table"""

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(
        db.DateTime(timezone=True), default=func.now()  # pylint: disable=E1102
    )
    messages = db.relationship("Message", backref="chat", lazy=True)


class Message(db.Model):
    """Message Table"""

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True), default=func.now()  # pylint: disable=E1102
    )
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"))


################################################################
####################### Create Flask App #######################
################################################################

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "hR7kT9Lc2M1qW8pZ4dF5jV0B3YxC6G"  # Arbitrary for now
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    # Imports required for correct database initialization
    # from .models import Chat, Message  # pylint: disable=W0611:unused-import
    create_db(app)
    init_chatbot(app)

    @app.route("/", methods=["GET", "POST"])
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


    @app.route("/reset_chat", methods=["POST"])
    def reset_chat():
        print("reset_chat")
        # Reset the chatbot (start with fresh memory)
        init_chatbot(current_app)
        # Clear the sqlite database with saved chats and messages
        Message.query.delete()
        Chat.query.delete()
        db.session.commit()
        return jsonify(status="success", message="Chat cleared!")

    return app



def init_chatbot(app):
    chat_id = "1"
    llm_config = {"configurable": {"thread_id": chat_id}}
    # llm = ChatOpenAI(temperature=0.0, api_key=API_KEY, model="gpt-3.5-turbo")
    llm = ChatOpenAI(temperature=0.0, api_key=API_KEY, model="gpt-5-mini")
    

    def call_model(state: MessagesState):
        system_msg_str = """
        You are a helpful assistant that answers truthfully. 
        All answers you give hav to be appropriately formatted in markdown format. 
        Format nested lists in markdown correctly and use indentation for subpoints under numbered lists.
        Dont use markdown formatted lists if nothing is listed.
        For mathematical expressions use single $ for inline math expressions and $$ for bigger math inserts. 
        Make sure all opened mathematical expressions are closed accordingly.
        Dont use '>!' and '!<' in your response.
        If you provide an enumerated list, then space them so that rendering it to html will result in a separate line
        for each entry.
        """
        messages = [SystemMessage(content=system_msg_str)] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": response}

    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)

    memory = MemorySaver()
    chatbot = workflow.compile(checkpointer=memory)

    app.config["chat_bot"] = chatbot
    app.config["llm_config"] = llm_config


def create_db(app):
    # from .models import Chat, Message  # pylint: disable=W0611:unused-import
    if not os.path.exists(f"website/{DB_NAME}"):
        with app.app_context():
            db.create_all()
        print("Database created!")
