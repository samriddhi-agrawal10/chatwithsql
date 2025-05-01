# from dotenv import load_dotenv
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.runnables import RunnablePassthrough
# from langchain_community.utilities import SQLDatabase
# from langchain_core.output_parsers import StrOutputParser
# import mysql.connector
# import streamlit as st
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
#     try:
#         connection = mysql.connector.connect(
#             user=user,
#             password=password,
#             host=host,
#             port=port,
#             database=database,
#             pool_name="mypool",  # Shortened pool name to avoid errors
#             pool_size=20
#         )
        
#         db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
#         db = SQLDatabase.from_uri(db_uri)
        
#         st.session_state.db_connection = connection  # Store raw connection in session state
#         return db
#     except mysql.connector.Error as err:
#         st.error(f"MySQL Connection Error: {err}")
#         return None
#     except Exception as e:
#         st.error(f"Error connecting to database: {e}")
#         return None


# def get_sql_chain(db):
#     template = """
#     You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
#     Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
#     STRICT RULES:
#     - Only use tables that exist in the schema.
#     - Do NOT assume there is a table named 'HumanMessage' or 'AIMessage'.
#     - Do NOT include explanations.
#     - Do NOT use markdown formatting (no triple backticks).
#     - Do NOT include "SQL Query:" before the query.
#     - Only output the valid SQL query.
#     - Give me output in tabular format.
#     <SCHEMA>{schema}</SCHEMA>
    
#     Conversation History: {chat_history}
    
#     Your turn:
    
#     Question: {question}
#     SQL Query:
#     """
    
#     prompt = ChatPromptTemplate.from_template(template)
#     llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
#     # llm = OllamaLLM(model="llama3.2:1b", base_url="http://localhost:11434")
    
#     def get_schema(_):
#         return db.get_table_info()
    
#     # print(( RunnablePassthrough.assign(schema=get_schema) | prompt | llm | StrOutputParser() )) #Logging the pipeline
#     return (
#         RunnablePassthrough.assign(schema=get_schema)
#         | prompt
#         | llm
#         | StrOutputParser()
#     )

# def get_response(user_query: str, chat_history: list):
#     if "db_connection" not in st.session_state or st.session_state.db_connection is None:
#         st.error("Database connection lost. Please reconnect.")
#         return "Database connection lost. Please reconnect."

#     db = st.session_state.db_connection
#     sql_chain = get_sql_chain(db)
    
#     query = sql_chain.invoke({
#         "question": user_query,
#         "chat_history": chat_history,
#     }).strip()
#     if query:
#         try:
#             match = re.search(r'```sql\n(.*?)```', query, re.DOTALL)
#             if match:
#                 query = match.group(1).strip()
#             response = db.run(query)
#             # print(response)
#             # # Convert raw data to DataFrame
#             # df = pd.DataFrame(response, columns=['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6'])
#             # # Print DataFrame
#             # print(df)
#         except Exception as e:
#             # st.error(f"Error executing query: {e}")
#             response = f"Error executing query: {e}"
#     else:
#         response = "No valid SQL query generated."
#     # print(type(response))
#     return response

# # Generate graphs
# def generate_graph(df, x_col, y_col, graph_type):
#     fig, ax = plt.subplots()
#     if graph_type == "Bar Chart":
#         sns.barplot(x=df[x_col], y=df[y_col], ax=ax)
#     elif graph_type == "Line Chart":
#         sns.lineplot(x=df[x_col], y=df[y_col], ax=ax)
#     elif graph_type == "Pie Chart":
#         df.set_index(x_col)[y_col].plot(kind='pie', autopct='%1.1f%%', ax=ax)
#     st.pyplot(fig)



# # Initialize chat history
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = [
#         AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
#     ]

# load_dotenv()

# st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")

# st.title("Chat with MySQL")

# # Sidebar settings
# with st.sidebar:
#     st.subheader("Settings")
#     st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")

#     st.text_input("Host", value="localhost", key="Host")
#     st.text_input("Port", value="3306", key="Port")
#     st.text_input("User", value="root", key="User")
#     st.text_input("Password", type="password", value="", key="Password")
#     st.text_input("Database", value="classicmodels", key="Database")

#     if st.button("Connect"):
#         with st.spinner("Connecting to database..."):
#             db = init_database(
#                 st.session_state["User"],
#                 st.session_state["Password"],
#                 st.session_state["Host"],
#                 st.session_state["Port"],
#                 st.session_state["Database"]
#             )
#             if db:
#                 st.success("Connected to database!")
#                 st.session_state.db_connection = db


# # Display chat history
# for message in st.session_state.chat_history:
#     if isinstance(message, AIMessage):
#         with st.chat_message("AI"):
#             st.markdown(message.content)
#     elif isinstance(message, HumanMessage):
#         with st.chat_message("Human"):
#             st.markdown(message.content)

# # User input and response handling
# user_query = st.chat_input("Type a message...")
# if user_query and user_query.strip():
#     st.session_state.chat_history.append(HumanMessage(content=user_query))

#     with st.chat_message("Human"):
#         st.markdown(user_query)

#     with st.chat_message("AI"):
#         response = get_response(user_query, st.session_state.chat_history)
#         st.write(response)

#     st.session_state.chat_history.append(AIMessage(content=response))


from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
import mysql.connector
import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    try:
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            pool_name="mypool",
            pool_size=20
        )
        
        db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        db = SQLDatabase.from_uri(db_uri)
        
        st.session_state.db_connection = connection
        return db
    except mysql.connector.Error as err:
        st.error(f"MySQL Connection Error: {err}")
        return None
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

def get_sql_chain(db):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    STRICT RULES:
    - Only use tables that exist in the schema.
    - Do NOT assume there is a table named 'HumanMessage' or 'AIMessage'.
    - Do NOT include explanations.
    - Do NOT use markdown formatting (no triple backticks).
    - Do NOT include "SQL Query:" before the query.
    - Only output the valid SQL query.
    - Give me output in tabular format.
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    
    def get_schema(_):
        return db.get_table_info()
    
    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query: str, chat_history: list):
    if "db_connection" not in st.session_state or st.session_state.db_connection is None:
        st.error("Database connection lost. Please reconnect.")
        return "Database connection lost. Please reconnect."

    db = st.session_state.db_connection
    sql_chain = get_sql_chain(db)
    
    query = sql_chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    }).strip()
    if query:
        try:
            match = re.search(r'```sql\n(.*?)```', query, re.DOTALL)
            if match:
                query = match.group(1).strip()
            response = db.run(query)
        except Exception as e:
            response = f"Error executing query: {e}"
    else:
        response = "No valid SQL query generated."
    return response

def generate_graph(df, x_col, y_col, graph_type):
    fig, ax = plt.subplots()
    if graph_type == "Bar Chart":
        sns.barplot(x=df[x_col], y=df[y_col], ax=ax)
    elif graph_type == "Line Chart":
        sns.lineplot(x=df[x_col], y=df[y_col], ax=ax)
    elif graph_type == "Pie Chart":
        df.set_index(x_col)[y_col].plot(kind='pie', autopct='%1.1f%%', ax=ax)
    st.pyplot(fig)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
    ]

load_dotenv()

st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")

# 🌙 Dark mode and WhatsApp-style chat CSS
st.markdown("""
    <style>
    body, .stApp {
        background-color: #000000;
        color: #f0f0f0;
    }

    section[data-testid="stSidebar"] {
        background-color: #000000;
        color: #f0f0f0;
    }

    .stMarkdown, .stTextInput > label, .stText, .stSubheader {
        color: #f0f0f0 !important;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: #2e2e2e;
        color: white;
        border: 1px solid #555;
    }

    .stChatMessage {
        max-width: 60%;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px 0;
        font-size: 15px;
        word-wrap: break-word;
    }

    .stChatMessage[data-testid="stChatMessage-Human"] {
        background-color: #075e54;
        color: white;
        margin-left: auto;
        text-align: right;
    }

    .stChatMessage[data-testid="stChatMessage-AI"] {
        background-color: #262d31;
        color: white;
        margin-right: auto;
        text-align: left;
    }

    .stMarkdown p {
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Chat with MySQL")

# Sidebar settings
with st.sidebar:
    st.subheader("Settings")
    st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")

    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="root", key="User")
    st.text_input("Password", type="password", value="", key="Password")
    st.text_input("Database", value="classicmodels", key="Database")

    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            if db:
                st.success("Connected to database!")
                st.session_state.db_connection = db

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

# User input and response handling
user_query = st.chat_input("Type a message...")
if user_query and user_query.strip():
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.chat_history)
        st.write(response)

    st.session_state.chat_history.append(AIMessage(content=response))
