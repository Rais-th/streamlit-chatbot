from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
import json
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

load_dotenv()

# Ensure the API key is loaded correctly
model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
openai_api_key = os.getenv('OPENAI_API_KEY')

if openai_api_key is None:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
else:
    # Load knowledge base
    def load_knowledge_base():
        with open('transport_data.json', 'r') as f:
            return json.load(f)

    knowledge_base = load_knowledge_base()

    def get_answer(question):
        for entry in knowledge_base:
            if question.lower() in entry['question'].lower():
                return entry['answer']
        return None

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
            if answer is None:
                # If no answer in knowledge base, use OpenAI model
                chatbot = ChatOpenAI(model=model, api_key=openai_api_key)
                response = chatbot(prompt)
                answer = response.choices[0].text.strip()

            st.session_state.messages.append(AIMessage(content=answer))

            with st.chat_message("assistant"):
                st.markdown(answer)

    if __name__ == "__main__":
        main()