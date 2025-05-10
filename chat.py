import streamlit as st
import speech_recognition as sr
from datetime import datetime
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone as pc
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os

# ------------------ API KEYS ------------------
PINECONE_API_KEY = "pcsk_6kCw69_TxKxRKuxhmHy9Fdx5ir8ty6p4XtrZySR9sfYj6XGgxBbUjVNjjQm5J2jmMs6hPt"
GROQ_API_KEY = "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"
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# ------------------ Streamlit Setup ------------------
st.set_page_config(layout="wide", page_title="Indian Constitution Chatbot", page_icon="📜")

# --------- Custom Styling ---------
st.markdown("""
<style>
.stApp {
    background-image: url('https://p4.wallpaperbetter.com/wallpaper/554/929/310/abstract-wood-wallpaper-preview.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.explorer-title {
    color:white;
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 5px;
}
.subtitle {
    color:white;
    text-align: center;
    font-size: 1.2rem;
    margin-bottom: 30px;
}
.stButton button {
    background-color: #9C2C2C;
    color: white;
    font-weight: bold;
}
.stButton button:hover {
    background-color: #B91C1C;
}
.content-card {
    background-color: black;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.flag-colors {
    display: flex;
    height: 10px;
    width: 100%;
    margin-bottom: 20px;
    border-radius: 5px;
    overflow: hidden;
}
.saffron { background-color: #FF9933; flex: 1; }
.white { background-color: #FFFFFF; flex: 1; }
.green { background-color: #138808; flex: 1; }
</style>
""", unsafe_allow_html=True)

# --------- Header ---------
st.markdown("<h1 class='explorer-title'>Indian Constitution ChatBot 📜</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ask Your Questions (by typing or speaking)</p>", unsafe_allow_html=True)

st.markdown("""
<div class='flag-colors'>
    <div class='saffron'></div>
    <div class='white'></div>
    <div class='green'></div>
</div>
""", unsafe_allow_html=True)

# --------- Chat History ---------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# --------- Load and Train Bot ---------
def load_and_train():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    pine = pc(api_key=PINECONE_API_KEY)
    index_name = 'constitution'
    docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)

    prompt_template = """You are a knowledgeable assistant specialized in the Indian Constitution. ONLY use the information provided in the CONTEXT to answer the user's question.
    - Do not rely on any external knowledge.
    - If the answer is not found in the context, politely say you don't have enough information.
    - Be accurate, clear, and concise.

    Context:
    {context}

    User's Question:
    {question}

    Your Answer (based ONLY on the above context):
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    llm = ChatGroq(model_name="llama3-70b-8192", api_key=GROQ_API_KEY, temperature=0.3)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_kwargs={"k": 12}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    st.session_state['qa'] = qa
    st.success("✅ Chatbot is Ready!")

# Load once
if "qa" not in st.session_state:
    with st.spinner("Setting up the Constitution Chatbot..."):
        load_and_train()

# --------- Microphone Handler ---------
r = sr.Recognizer()

def listen_and_convert():
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Please speak.")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            st.success(f"Recognized: {text}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return timestamp, text
        except sr.UnknownValueError:
            st.error("😕 Could not understand your speech.")
            return None, None
        except sr.RequestError as e:
            st.error(f"🔴 Google Speech Recognition error: {e}")
            return None, None

# --------- Input Section ---------
inputt = st.text_input("Type your Question:")

col1, col2 = st.columns(2)

with col1:
    if st.button("Submit Typed Question"):
        if inputt:
            with st.spinner("Generating answer..."):
                qa = st.session_state['qa']
                result = qa.invoke(inputt)
                st.success("Here’s the answer:")
                st.write(result['result'])
                st.session_state['chat_history'].append({"question": inputt, "answer": result['result']})
        else:
            st.warning("Please type something!")

with col2:
    if st.button("🎙️ Speak Your Question"):
        timestamp, spoken_text = listen_and_convert()
        if spoken_text:
            with st.spinner("Generating answer from your speech..."):
                qa = st.session_state['qa']
                result = qa.invoke(spoken_text)
                st.success("Here’s the answer:")
                st.write(result['result'])
                st.session_state['chat_history'].append({"question": spoken_text, "answer": result['result']})

# --------- Chat History Section ---------
if st.session_state['chat_history']:
    st.markdown("## 💬 Chat History")
    with st.expander("View Previous Conversations", expanded=True):
        for i, entry in enumerate(st.session_state['chat_history']):
            st.write(f"**{i+1}. Question:** {entry['question']}")
            st.write(f"**Answer:** {entry['answer']}")
            st.divider()
