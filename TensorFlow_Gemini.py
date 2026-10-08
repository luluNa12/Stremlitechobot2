
# Import libraries
import streamlit as st
import time
import tensorflow as tf
import requests


# 1) Load TensorFlow router model once
@st.cache_resource
def load_router():
    model = tf.keras.models.load_model("tf_router_model.keras")

    with open("labels.txt", "r", encoding="utf-8") as f:
        labels = [line.strip() for line in f.readlines()]

    return model, labels


router_model, router_labels = load_router()


# 2) Predict topic using TensorFlow
def predict_topic(text):
    x = tf.constant([str(text)])
    probs = router_model.predict(x, verbose=0)[0]
    return router_labels[int(probs.argmax())]


# 3) Topic instructions
def topic_instruction(topic):
    if topic == "excel":
        return (
            "Answer ONLY for Excel. Give short step-by-step "
            "Excel menu clicks. Do NOT mention Python or R."
        )

    if topic == "r":
        return (
            "Answer ONLY for R. Keep it short and clear. "
            "Do NOT mention Python or Excel."
        )

    if topic == "python":
        return (
            "Answer ONLY for Python. Focus on troubleshooting steps. "
            "Do NOT mention Excel or R."
        )

    if topic == "course":
        return (
            "Answer like an instructor for the course. "
            "Keep it short and professional."
        )

    return "Answer normally."


# 4) Google Gemini API
def ai_ask(prompt):
    api_key = st.secrets["GEMINI_API_KEY"]

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.5-flash-lite:generateContent"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 500
        }
    }

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 429:
            return "API usage limit reached. Please try again later."

        response.raise_for_status()
        data = response.json()

        parts = data["candidates"][0]["content"]["parts"]
        return "".join(part.get("text", "") for part in parts)

    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

    except (KeyError, IndexError):
        return "No response was returned by Gemini."


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


# 6) Streamlit user interface
st.title("Lina Shoshani - TensorFlow + Google Gemini AI Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Power BI dashboard
with st.chat_message("assistant"):
    st.image(
        "PowerBiDashboard.png",
        caption="CIT 144 – Demographics Data Visualization"
    )

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Accept user input
prompt = st.chat_input("What is up?")

if prompt:
    # Predict topic
    topic = predict_topic(prompt)

    # Display predicted topic
    st.caption(f"Predicted topic: {topic}")

    # Save and display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Gemini response
    with st.chat_message("assistant"):
        if "GEMINI_API_KEY" not in st.secrets:
            response = "Please configure your Gemini API key."
            st.error(response)
        else:
            response = st.write_stream(
                response_generator(prompt, topic)
            )

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
