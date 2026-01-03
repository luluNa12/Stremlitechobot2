import streamlit as st
import random
import time

# Streamed response emulator
def response_generator():
    response = ai_ask("Pretend you are a very friendly and helpful person.  Please provide a response given the provided context.  Please provide the response only with no before or after commentary.",
                      data=st.session_state.messages,
                      api_key=st.secrets["apikey"])
    for word in response.split():
        yield word + " "
        time.sleep(0.05)



st.title("AI chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display assistant response in chat message container
with st.chat_message("assistant"):
    response = st.write_stream(response_generator())

# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": response})
