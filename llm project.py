import streamlit as st
import random
import time
from langchain import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
from langchain.chat_models import ChatOpenAI

# Set up your Databricks SQLDatabase connection
catalog = "main"
schema = "ai_chatbot"
server_hostname = "adb-7701630258100873.13.azuredatabricks.net"
api_token = "dapidbe48c124b0e8fd83d88080a2ed34034-3"
warehouse_id = "d02a308bd9e9096c"
db_databricks = SQLDatabase.from_databricks(
    catalog=catalog,
    schema=schema,
    host=server_hostname,
    api_token=api_token,
    warehouse_id=warehouse_id,
)

# Set up the OpenAI instance
OPENAI_API_KEY = "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"
llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo-16k', openai_api_key=OPENAI_API_KEY)

# Set up the SQLDatabaseChain
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db_databricks, verbose=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("You:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(f"You: {prompt}")

    # Get assistant response from OpenAI and SQLDatabaseChain
    assistant_response = db_chain.run(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
