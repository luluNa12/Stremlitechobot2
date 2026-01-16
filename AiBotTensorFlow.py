#import libraries
import streamlit as st
import time
import tensorflow as tf
import requests
import json

# 1) Load router model once
@st.cache_resource
def load_router():
    model = tf.keras.models.load_model("tf_router_model.keras")
    with open("labels.txt", "r", encoding="utf-8") as f:
        labels = [line.strip() for line in f.readlines()]
    return model, labels


router_model, router_labels = load_router()


# 2) Predict topic
def predict_topic(text):
    text = str(text)
    x = tf.constant([text])  # TensorFlow string tensor
    probs = router_model.predict(x, verbose=0)[0]
    return router_labels[int(probs.argmax())]

#3) Topic instructions
def topic_instruction(topic):
    if topic == "excel":
        return "Answer ONLY for Excel. Give short step-by-step Excel menu clicks. Do NOT mention Python or R."
    if topic == "r":
        return "Answer ONLY for R. Keep it short and clear. Do NOT mention Python or Excel."
    if topic == "python":
        return "Answer ONLY for Python. Focus on troubleshooting steps. Do NOT mention Excel or R."
    if topic == "course":
        return "Answer like an instructor for the course. Keep it short and professional."
    return "Answer normally."

# 4) LLM call (Mistral)
def ai_ask(
    prompt,
    temperature=0.5,
    max_tokens=250,
    model="mistral-small-latest",
    api_url="https://api.mistral.ai/v1/chat/completions",
):
    api_key = st.secrets["apikey"]

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(temperature),
        "model": model,
        "max_tokens": int(max_tokens),
    }
  
    headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
        response = requests.post(api_url, headers=headers, json=payload)
    
        if response.status_code == 429:
            return "Rate limit reached. Please try again in a minute."
    
        try:
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling API: {str(e)}"
          
# 5) Stream response generator
def response_generator(user_prompt, topic):
    instruction = topic_instruction(topic)

    full_prompt = (
        "Pretend you are a very friendly and helpful person.\n"
        + instruction
        + "\n\nUser question:\n"
        + user_prompt
    )

    response_text = ai_ask(full_prompt)

    for word in response_text.split():
        yield word + " "
        time.sleep(0.03)

# 6) Streamlit UI
st.title("Lina Shoshani - AI chat")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the dashboard image once at the top
with st.chat_message("assistant"):
    st.image("PowerBiDashboard.png", caption="CIT 144 – Demographics Data Visualization")

# Render previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
prompt = st.chat_input("What is up?")

if prompt:
    # Predict topic
    topic = predict_topic(prompt)

    # Show predicted topic so you can test your router
    st.caption(f"Predicted topic: {topic}")
 # Save and show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream assistant reply
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt, topic))

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": response})






