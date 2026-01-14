import streamlit as st
import random
import time
import tensorflow as tf

@st.cache_resource
def load_router():
    model = tf.keras.models.load_model("tf_router_model.keras")
    labels = [line.strip() for line in open("labels.txt")]
    # labels = [line.strip() for line in open("labels.txt","r")]
    return model, labels

router_model, router_labels = load_router()

#Predict:
import numpy as np

def predict_topic(text):
    text = str(text)                    #force string
    x = np.array([text])                 # <-- this is the fix
    probs = router_model.predict(x, verbose=0)[0]
    return router_labels[int(probs.argmax())]



def topic_instruction(topic):
    if topic == "excel":
        return "Answer using simple Excel steps and menu clicks. Keep it short."
    if topic == "r":
        return "Answer using simple R steps. Explain functions in plain language."
    if topic == "python":
        return "Answer with Python troubleshooting steps. Ask for the exact error if needed."
    if topic == "course":
        return "Answer like an instructor. Keep it short and professional."
    return "Answer normally."




import requests
import json

def ai_ask(prompt, data=None, temperature=0.5, max_tokens=250, model="mistral-small-latest", api_key=None, api_url="https://api.mistral.ai/v1/chat/completions"):
    if api_key is None or api_url is None:
        if "idToken" in globals():
            api_key = globals()["idToken"]
            api_url = "https://llm.boardflare.com"
        else:
            return "Login on the Functions tab for limited demo usage, or sign up for a free Mistral AI account at https://console.mistral.ai/ and add your own api_key."

    if not isinstance(temperature, (float, int)) or not (0 <= float(temperature) <= 2):
        return "Error: temperature must be a float between 0 and 2 (inclusive)"
    if not isinstance(max_tokens, (float, int)) or not (5 <= float(max_tokens) <= 5000):
        return "Error: max_tokens must be a number between 5 and 5000 (inclusive)"

    # Construct the message incorporating both prompt and data if provided
    message = prompt
    if data is not None:
        data_str = json.dumps(data, indent=2)
        message += f"\n\nData to analyze:\n{data_str}"

    # Prepare the API request payload
    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": float(temperature),
        "model": model,
        "max_tokens": int(max_tokens)
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the API request
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 429:
        return "You have hit the rate limit for the API. Please try again later."
    try:
        response.raise_for_status()
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        return content
    except Exception as e:
        return f"Error: {str(e)}"


def response_generator(user_prompt, topic):
    instruction = topic_instruction(topic)

    full_prompt = (
        "Pretend you are a very friendly and helpful person.\n"
        + instruction
        + "\n\nUser question:\n"
        + user_prompt
    )

    response = ai_ask(
        full_prompt,
        data=st.session_state.messages,
        api_key=st.secrets["apikey"]
    )

    for word in response.split():
        yield word + " "
        time.sleep(0.05)




st.title("Lina Shoshani - AI chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the dashboard image once at the top
with st.chat_message("assistant"):
    st.image("PowerBiDashboard.png", caption="CIT 144 – Demographics Data Visualization")


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
# Accept user input
if prompt := st.chat_input("What is up?"):
    topic = predict_topic(prompt)

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt, topic))

    st.session_state.messages.append({"role": "assistant", "content": response})



