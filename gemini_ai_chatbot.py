
import streamlit as st
import requests
import time

# Google Gemini AI
def ai_ask(messages, api_key):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.5-flash-lite:generateContent"
    )

    contents = []

    for message in messages:
        role = "model" if message["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": message["content"]}]
        })

    payload = {
        "contents": contents,
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


def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("AI Chat - Google Gemini")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display dashboard image
with st.chat_message("assistant"):
    st.image(
        "DashboardImage.png",
        caption="CIT 144 – Demographics Data Visualization"
    )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("assistant"):
        if "GEMINI_API_KEY" not in st.secrets:
            response = "Please configure your Gemini API key."
            st.error(response)
        else:
            answer = ai_ask(
                st.session_state.messages,
                st.secrets["GEMINI_API_KEY"]
            )
            response = st.write_stream(
                response_generator(answer)
            )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
