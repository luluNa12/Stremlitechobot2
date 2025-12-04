import streamlit as st
import panda as np

with st.chat_message("Lina"):
    st.write("Hello 👋")
    
with st.chat_message("Shoshani"):    
    st.write("Thank you ♡")


import streamlit as st

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
