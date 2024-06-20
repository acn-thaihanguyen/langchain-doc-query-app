import os

import streamlit as st
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from llama_index.core import VectorStoreIndex
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

llama_debug = LlamaDebugHandler(print_trace_on_end=True)
callback_manager = CallbackManager(handlers=[llama_debug])
Settings.llm = OpenAI(model=os.environ["OPENAI_MODEL"], temperature=0)
Settings.embed_model = OpenAIEmbeddings(model=os.environ["OPENAI_EMBEDED_MODEL"])
Settings.callback_manager = callback_manager


@st.cache_resource(show_spinner=False)
def get_index() -> VectorStoreIndex:
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    pinecone_index = pc.Index(name="langchain-doc-query-app")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
    )
    return index


index = get_index()

if "chat_engine" not in st.session_state.keys():
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode=ChatMode.CONTEXT,
        verbose=True,
    )

st.set_page_config(
    page_title="langchain-learning-assistant-chatbot",
    page_icon=":robot:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.title("LangChain Learning Assistant💬")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Aske me any questions about Langchain's documentation!",
        }
    ]

prompt = st.chat_input("Your question: ")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking ..."):
            response = st.session_state.chat_engine.chat(message=prompt)
            st.write(response.response)

            st.session_state.messages.append(
                {"role": "assistant", "content": response.response}
            )
