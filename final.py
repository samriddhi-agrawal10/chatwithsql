import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
import mysql.connector
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Load environment variables
load_dotenv()

# LangSmith tracing
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "streamlit-sql-chatbot"

chat_history = [
    AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database.")
]

db_connection = None
db = None

def init_database(user, password, host, port, database):
    global db_connection, db
    try:
        db_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port)
        )
        db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        db = SQLDatabase.from_uri(db_uri)
        return "✅ Connected to database!"
    except mysql.connector.Error as err:
        return f"❌ MySQL Error: {err}"
    except Exception as e:
        return f"❌ Connection Error: {e}"

def get_sql_chain(db):
    template = """
    You are a data analyst. Given a user's question and the database schema, write a SQL query.

    STRICT RULES:
    - Only use tables from schema.
    - No explanations.
    - No markdown or triple backticks.
    - Just return the raw SQL query.

    <SCHEMA>{schema}</SCHEMA>
    History: {chat_history}
    Question: {question}
    SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    def get_schema(_):
        return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query, debug=False):
    global db
    if db is None:
        return "❌ Database not connected."

    sql_chain = get_sql_chain(db)

    # Run the chain to get SQL query
    query = sql_chain.invoke({
        "question": user_query,
        "chat_history": [msg.content for msg in chat_history],
    }).strip()

    # Clean up LLM output
    query = query.strip().strip("`")
    query = re.sub(r"^sql\s*", "", query, flags=re.IGNORECASE).strip()

    if debug:
        st.markdown("🔍 **Generated SQL:**")
        st.code(query, language="sql")

    if query:
        try:
            response = db.run(query)
            if not response:
                return "⚠️ Query ran but returned no results."
            if isinstance(response, list):
                df = pd.DataFrame(response)
                return df
            return str(response)
        except Exception as e:
            return f"❌ Query execution failed: {e}"
    else:
        return "⚠️ No valid SQL query generated."

def plot_graph(df, x_col, y_col, graph_type):
    fig, ax = plt.subplots()
    if graph_type == "Bar Chart":
        sns.barplot(x=df[x_col], y=df[y_col], ax=ax)
    elif graph_type == "Line Chart":
        sns.lineplot(x=df[x_col], y=df[y_col], ax=ax)
    elif graph_type == "Pie Chart":
        df.set_index(x_col)[y_col].plot(kind='pie', autopct='%1.1f%%', ax=ax)
    st.pyplot(fig)

# ------------------- STREAMLIT UI ---------------------

st.set_page_config(page_title="SQL Chatbot with Gemini", layout="wide")
st.title("💬 SQL Chatbot (Gemini + Streamlit)")

with st.expander("⚙️ Connect to Database", expanded=True):
    host = st.text_input("Host", "localhost")
    port = st.text_input("Port", "3306")
    user = st.text_input("User", "root")
    password = st.text_input("Password", type="password")
    database = st.text_input("Database", "classicmodels")

    if st.button("🔌 Connect"):
        status = init_database(user, password, host, port, database)
        st.info(status)

st.markdown("---")
st.subheader("📨 Ask Your Database")
user_input = st.text_input("Your Question")
debug = st.checkbox("Show raw LLM SQL output")

if user_input:
    chat_history.append(HumanMessage(content=user_input))
    response = get_response(user_input, debug=debug)
    chat_history.append(AIMessage(content=str(response)))

    if isinstance(response, pd.DataFrame):
        st.dataframe(response)
        if not response.empty:
            with st.expander("📊 Visualize Data"):
                cols = response.columns.tolist()
                x_col = st.selectbox("X-axis", cols)
                y_col = st.selectbox("Y-axis", cols, index=min(1, len(cols)-1))
                chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Pie Chart"])
                if st.button("Generate Chart"):
                    plot_graph(response, x_col, y_col, chart_type)
    else:
        st.write(response)
