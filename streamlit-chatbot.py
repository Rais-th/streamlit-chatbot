import os
import streamlit as st
from datetime import datetime
import openai
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')

def main():
    st.title("Streamlit Chatbot")
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content=f"The current date is: {datetime.now().date()}")
        ]

    for message in st.session_state.messages:
        with st.chat_message(message.type):
            st.markdown(message.content)

    if prompt := st.chat_input("What would you like to do today?"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response['choices'][0]['message']['content']
        except Exception as e:
            answer = f"Error: {str(e)}"
        st.session_state.messages.append(AIMessage(content=answer))
        with st.chat_message("ai"):
            st.markdown(answer)

if __name__ == "__main__":
    main()
