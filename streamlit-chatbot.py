from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
import json
import os
import openai  # Import the openai module

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

load_dotenv()

# Ensure the API key is loaded correctly
model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
openai_api_key = os.getenv('OPENAI_API_KEY')

if openai_api_key is None:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
else:
    openai.api_key = openai_api_key
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt="Say hello!",
            max_tokens=5
        )
        print("API Key works correctly:", response.choices[0].text.strip())
    except Exception as e:
        print("Error with API Key:", e)

    # Load knowledge base with error handling
    def load_knowledge_base():
        try:
            with open('transport_data.json', 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"Error loading knowledge base: {e}")
            return []

    knowledge_base = load_knowledge_base()

    def get_answer(question):
        for entry in knowledge_base:
            if question.lower() in entry['question'].lower():
                return entry['answer']
        return "Sorry, I don't have an answer for that."

    def main():
        st.title("Streamlit Chatbot")

        if "messages" not in st.session_state:
            st.session_state.messages = [
                SystemMessage(content=f"The current date is: {datetime.now().date()}")
            ]

        for message in st.session_state.messages:
            message_json = json.loads(message.json())
            with st.chat_message(message_json["type"]):
                st.markdown(message_json["content"])

        if prompt := st.chat_input("What would you like to do today?"):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append(HumanMessage(content=prompt))

            # First check the knowledge base
            answer = get_answer(prompt)
            if answer == "Sorry, I don't have an answer for that.":
                # If no answer in knowledge base, use OpenAI model
                chatbot = ChatOpenAI(model=model, api_key=openai_api_key)
                response = chatbot(prompt)
                answer = response.choices[0].text.strip()

            st.session_state.messages.append(AIMessage(content=answer))

            with st.chat_message("assistant"):
                st.markdown(answer)

    if __name__ == "__main__":
        main()