import streamlit as st
import numpy as np

with st.chat_message("Lina"):
    st.write("Hello 👋")
    
with st.chat_message("Shoshani"):    
    st.write("Thank you ♡")

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

