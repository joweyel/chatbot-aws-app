import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import SystemMessage


db = SQLAlchemy()
DB_NAME = "database.db"
API_KEY = os.getenv("OPENAI_API_KEY")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "hR7kT9Lc2M1qW8pZ4dF5jV0B3YxC6G"  # Arbitrary for now
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    create_db(app)

    init_chatbot(app)

    from .views import views

    app.register_blueprint(views, url_prefix="/")

    return app


def init_chatbot(app):
    chat_id = "1"
    llm_config = {"configurable": {"thread_id": chat_id}}
    llm = ChatOpenAI(temperature=0.0, api_key=API_KEY, model="gpt-3.5-turbo")

    def call_model(state: MessagesState):
        system_msg_str = """
        You are a helpful assistant that answers truthfully. 
        All answers you give hav to be appropriately formatted in markdown format. 
        Format nested lists in markdown correctly and use indentation for subpoints under numbered lists.
        Dont use markdown formatted lists if nothing is listed.
        For mathematical expressions use single $ for inline math expressions and $$ for bigger math inserts.
        Dont use '>!' and '!<' in your response.
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
    if not os.path.exists(f"website/{DB_NAME}"):
        with app.app_context():
            db.create_all()
        print("Database created!")
