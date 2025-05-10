# home.py - Landing page for the Constitution Chatbot

import streamlit as st

# ------------------ Page Configuration ------------------
st.set_page_config(page_title="Legal Ease", page_icon="📜", layout="wide")

# ------------------ Background and Styling ------------------
def add_custom_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://p4.wallpaperbetter.com/wallpaper/554/929/310/abstract-wood-wallpaper-preview.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
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
        .title-text {
            color: white;
            font-size: 3rem;
            text-align: center;
            text-shadow: 3px 3px 6px black;
            margin-top: 20px;
            margin-bottom: 40px;
            font-weight: bold;
        }
        .feature-card {
            background-color: black;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            color: white;
        }
        .nav-button {
            display: inline-block;
            padding: 15px 30px;
            margin: 15px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background-color: #9C2C2C;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            transition: background-color 0.3s, transform 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .nav-button:hover {
            background-color: #B91C1C;
            transform: translateY(-3px);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------ Main App ------------------
def app():
    add_custom_styles()
    
    # Title
    st.markdown("<h1 class='title-text'>LEGAL EASE 📜</h1>", unsafe_allow_html=True)

    # Tricolor Flag Bar
    st.markdown("""
    <div class='flag-colors'>
        <div class='saffron'></div>
        <div class='white'></div>
        <div class='green'></div>
    </div>
    """, unsafe_allow_html=True)


    # Introduction
    st.markdown(
        """
        <div class='feature-card'>
        <h2>Welcome to the Indian Constitution Interactive Guide</h2>
        <p>Explore the world's longest written constitution through our interactive platform. 
        Ask questions, get instant answers, and deepen your understanding of India's foundational document.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Features
    st.markdown(
        """
        <div class='feature-card'>
        <h3>📱 Features</h3>
        <ul>
            <li><b>AI-Powered Chat:</b> Ask any question about the Indian Constitution</li>
            <li><b>Voice Input:</b> Speak your questions for hands-free interaction</li>
            <li><b>Constitution Explorer:</b> Browse through different articles and sections</li>
            <li><b>Chat History:</b> Review your previous conversations anytime</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation Options
    st.markdown("<h3 style='text-align: center; color: white;'>Choose a Module</h3>", unsafe_allow_html=True)
    
    col1, col2= st.columns(2)
    with col1:
        if st.button("🗣️ Chat with Constitution"):
            st.switch_page("pages/chat.py")
    with col2:
        if st.button("📖 Constitution Explorer"):
            st.switch_page("pages/explorer.py")


    # About Section
    st.markdown(
        """
        <div class='feature-card'>
        <h3>ℹ️ About</h3>
        <p>This application uses advanced AI technology powered by LLaMA-3 to provide accurate information about the Indian Constitution.
        The system references the complete text of the Constitution, ensuring reliable and precise answers to your questions.</p>
        <p><small>Created with ❤️ using Streamlit, LangChain, Pinecone, and Groq</small></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    app()
