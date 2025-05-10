# explorer.py - Module 3: Constitution explorer for browsing different sections

import streamlit as st
import pandas as pd
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone as pc
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os

def app():
    # Set background and styling
    set_page_styling()
    
    # Page header
    st.markdown("<h1 class='explorer-title'>📜 Constitution Explorer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Browse through different parts of the Indian Constitution</p>", unsafe_allow_html=True)
    
    # Initialize QA system if not already done
    if "qa" not in st.session_state:
        with st.spinner("Setting up the Constitution Explorer..."):
            initialize_qa_system()
    
    # Sidebar for navigation
    with st.sidebar:
        st.markdown("### Navigation")
        
        explorer_option = st.radio(
            "Select View",
            ["Parts Overview", "Fundamental Rights", "Directive Principles", 
             "Constitutional Bodies", "Amendments", "Search by Article"]
        )
    
    # Main content
    if explorer_option == "Parts Overview":
        display_parts_overview()
    elif explorer_option == "Fundamental Rights":
        display_fundamental_rights()
    elif explorer_option == "Directive Principles":
        display_directive_principles()
    elif explorer_option == "Constitutional Bodies":
        display_constitutional_bodies()
    elif explorer_option == "Amendments":
        display_amendments()
    elif explorer_option == "Search by Article":
        search_by_article()

def set_page_styling():
    """Apply custom styling to the explorer interface"""
    st.markdown(
        """
        <style>
        .stApp {
            background-image:url('https://p4.wallpaperbetter.com/wallpaper/554/929/310/abstract-wood-wallpaper-preview.jpg');
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
        .content-card {
            background-color:black;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .part-card {
            background-color:black;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 5px solid #9C2C2C;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .part-card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        .article-result {
            background-color:black;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 5px solid #1E40AF;
        }
        .stButton button {
            background-color: #9C2C2C;
            color: white;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #B91C1C;
        }
        .flag-colors {
            display: flex;
            height: 10px;
            width: 100%;
            margin-bottom: 20px;
            border-radius: 5px;
            overflow: hidden;
        }
        .saffron {
            background-color: #FF9933;
            flex: 1;
        }
        .white {
            background-color: #FFFFFF;
            flex: 1;
        }
        .green {
            background-color: #138808;
            flex: 1;
        }
        .timeline {
            position: relative;
            max-width: 1200px;
            margin: 0 auto;
        }
        .timeline::after {
            content: '';
            position: absolute;
            width: 6px;
            background-color: white;
            top: 0;
            bottom: 0;
            left: 50%;
            margin-left: -3px;
        }
        .amendment-card {
            padding: 10px 40px;
            position: relative;
            background-color:white;
            width: 50%;
        }
        .amendment-card::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            right: -10px;
            background-color: white;
            border: 4px solid #9C2C2C;
            top: 15px;
            border-radius: 50%;
            z-index: 1;
        }
        .left {
            left: 0;
        }
        .right {
            left: 50%;
        }
        .left::before {
            content: " ";
            height: 0;
            position: absolute;
            top: 22px;
            width: 0;
            z-index: 1;
            right: 30px;
            border: medium solid #F9F9F9;
            border-width: 10px 0 10px 10px;
            border-color: transparent transparent transparent #F9F9F9;
        }
        .right::before {
            content: " ";
            height: 0;
            position: absolute;
            top: 22px;
            width: 0;
            z-index: 1;
            left: 30px;
            border: medium solid #F9F9F9;
            border-width: 10px 10px 10px 0;
            border-color: transparent #F9F9F9 transparent transparent;
        }
        .right::after {
            left: -10px;
        }
        .amendment-content {
            padding: 20px 30px;
            background-color:black;
            position: relative;
            border-radius: 6px;
            border-left: 5px solid #9C2C2C;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def initialize_qa_system():
    """Initialize the QA system with LangChain and Pinecone"""
    # Load API keys
    PINECONE_API_KEY = "pcsk_6kCw69_TxKxRKuxhmHy9Fdx5ir8ty6p4XtrZySR9sfYj6XGgxBbUjVNjjQm5J2jmMs6hPt"
    GROQ_API_KEY = "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"
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    
    # Initialize embeddings and vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    pine = pc(api_key=PINECONE_API_KEY)
    
    index_name = 'constitution'
    docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)
    
    # Create prompt template for improved responses
    prompt_template = """You are a knowledgeable assistant specialized in the Indian Constitution.
    - Be accurate, clear, and concise.
    - Format your answer with appropriate Markdown for readability.
    - If relevant, cite specific Articles, Sections, or Parts of the Constitution.

    Context:
    {context}

    User's Question:
    {question}

    Your Answer:
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    llm = ChatGroq(model_name="llama3-70b-8192", api_key=GROQ_API_KEY, temperature=0.3)
    
    # Create RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_kwargs={"k": 12}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    st.session_state['qa'] = qa
    st.success("✅ Explorer is Ready!")

def display_parts_overview():
    """Display an overview of all parts of the constitution"""
    st.markdown("""
    <div class='flag-colors'>
        <div class='saffron'></div>
        <div class='white'></div>
        <div class='green'></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("## Parts of the Indian Constitution")
    st.markdown("The Constitution of India is divided into 22 parts, each containing related articles.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Parts data
    parts_data = [
        {"number": "I", "title": "The Union and its Territory", "articles": "1-4"},
        {"number": "II", "title": "Citizenship", "articles": "5-11"},
        {"number": "III", "title": "Fundamental Rights", "articles": "12-35"},
        {"number": "IV", "title": "Directive Principles of State Policy", "articles": "36-51"},
        {"number": "IVA", "title": "Fundamental Duties", "articles": "51A"},
        {"number": "V", "title": "The Union", "articles": "52-151"},
        {"number": "VI", "title": "The States", "articles": "152-237"},
        {"number": "VII", "title": "The States in Part B of the First Schedule", "articles": "238 (Repealed)"},
        {"number": "VIII", "title": "The Union Territories", "articles": "239-242"},
        {"number": "IX", "title": "The Panchayats", "articles": "243-243O"},
        {"number": "IXA", "title": "The Municipalities", "articles": "243P-243ZG"},
        {"number": "IXB", "title": "The Co-operative Societies", "articles": "243ZH-243ZT"},
        {"number": "X", "title": "The Scheduled and Tribal Areas", "articles": "244-244A"},
        {"number": "XI", "title": "Relations between the Union and the States", "articles": "245-263"},
        {"number": "XII", "title": "Finance, Property, Contracts and Suits", "articles": "264-300A"},
        {"number": "XIII", "title": "Trade, Commerce and Intercourse within India", "articles": "301-307"},
        {"number": "XIV", "title": "Services under the Union and the States", "articles": "308-323"},
        {"number": "XIVA", "title": "Tribunals", "articles": "323A-323B"},
        {"number": "XV", "title": "Elections", "articles": "324-329A"},
        {"number": "XVI", "title": "Special Provisions for Certain Classes", "articles": "330-342"},
        {"number": "XVII", "title": "Official Language", "articles": "343-351"},
        {"number": "XVIII", "title": "Emergency Provisions", "articles": "352-360"},
        {"number": "XIX", "title": "Miscellaneous", "articles": "361-367"},
        {"number": "XX", "title": "Amendment of the Constitution", "articles": "368"},
        {"number": "XXI", "title": "Temporary, Transitional and Special Provisions", "articles": "369-392"},
        {"number": "XXII", "title": "Short Title, Commencement and Repeals", "articles": "393-395"}
    ]
    
    # Display parts as interactive cards
    for part in parts_data:
        st.markdown(
            f"""
            <div class='part-card'>
                <h3>Part {part['number']}: {part['title']}</h3>
                <p><strong>Articles:</strong> {part['articles']}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    # Option to explore a specific part
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### Explore a Part")
    
    selected_part = st.selectbox(
        "Select a part to explore:",
        [f"Part {part['number']}: {part['title']}" for part in parts_data]
    )
    
    if st.button("Explore Selected Part"):
        part_name = selected_part.split(":")[0].strip()
        with st.spinner(f"Fetching information about {part_name}..."):
            qa = st.session_state['qa']
            result = qa.invoke(f"Explain {part_name} of the Indian Constitution in detail")
            
            st.markdown("<div class='article-result'>", unsafe_allow_html=True)
            st.markdown(result['result'])
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_fundamental_rights():
    """Display information about fundamental rights"""
    st.markdown("""
    <div class='flag-colors'>
        <div class='saffron'></div>
        <div class='white'></div>
        <div class='green'></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("## Fundamental Rights (Articles 12-35)")
    st.markdown("Fundamental Rights are the basic human rights enshrined in the Constitution of India which are guaranteed to all citizens.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Fundamental rights data
    rights = [
        {"name": "Right to Equality (Articles 14-18)", "description": "Equality before law, prohibition of discrimination, equality of opportunity"},
        {"name": "Right to Freedom (Articles 19-22)", "description": "Freedom of speech, assembly, association, movement, residence, and profession"},
        {"name": "Right against Exploitation (Articles 23-24)", "description": "Prohibition of traffic in human beings and forced labor, prohibition of child labor"},
        {"name": "Right to Freedom of Religion (Articles 25-28)", "description": "Freedom of conscience and religion, freedom to manage religious affairs"},
        {"name": "Cultural and Educational Rights (Articles 29-30)", "description": "Protection of interests of minorities, right of minorities to establish educational institutions"},
        {"name": "Right to Constitutional Remedies (Article 32)", "description": "Right to move the Supreme Court for enforcement of Fundamental Rights"}
    ]
    
    # Display rights
    for right in rights:
        st.markdown(
            f"""
            <div class='part-card'>
                <h3>{right['name']}</h3>
                <p>{right['description']}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Option to explore a specific right
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### Explore a Fundamental Right")
    
    selected_right = st.selectbox(
        "Select a right to explore:",
        [right['name'] for right in rights]
    )
    
    if st.button("Learn More"):
        with st.spinner(f"Fetching information about {selected_right}..."):
            qa = st.session_state['qa']
            result = qa.invoke(f"Explain {selected_right} in detail as per the Indian Constitution")
            
            st.markdown("<div class='article-result'>", unsafe_allow_html=True)
            st.markdown(result['result'])
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_directive_principles():
    """Display information about directive principles of state policy"""
    st.markdown("""
    <div class='flag-colors'>
        <div class='saffron'></div>
        <div class='white'></div>
        <div class='green'></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("## Directive Principles of State Policy (Articles 36-51)")
    st.markdown("""
    The Directive Principles of State Policy are guidelines to the central and state governments of India, 
    to be kept in mind while framing laws and policies. These provisions, contained in Part IV of the Constitution, 
    are not enforceable by any court, but the principles laid down therein are fundamental in the governance of the country.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Directive principles categories
    categories = [
        {
            "name": "Socialist Principles",
            "articles": ["Article 38: State to secure a social order for the promotion of welfare of the people",
                         "Article 39: Certain principles of policy to be followed by the State",
                         "Article 39A: Equal justice and free legal aid"]
        },
        {
            "name": "Gandhian Principles",
            "articles": ["Article 40: Organization of village panchayats",
                         "Article 43: Living wage, etc., for workers",
                         "Article 48: Organization of agriculture and animal husbandry"]
        },
        {
            "name": "Liberal-Intellectual Principles",
            "articles": ["Article 44: Uniform civil code",
                         "Article 45: Provision for early childhood care and education to children below the age of six years",
                         "Article 50: Separation of judiciary from executive"]
        },
        {
            "name": "International Relations",
            "articles": ["Article 51: Promotion of international peace and security"]
        }
    ]
    
    # Display categories
    for category in categories:
        st.markdown(
            f"""
            <div class='part-card'>
                <h3>{category['name']}</h3>
                <ul>
                    {''.join([f'<li>{article}</li>' for article in category['articles']])}
                </ul>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Interactive exploration
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### Get Information on a Specific Article")
    
    article_number = st.number_input("Enter Article Number (36-51)", min_value=36, max_value=51, value=39)
    
    if st.button("Get Details"):
        with st.spinner(f"Fetching information about Article {article_number}..."):
            qa = st.session_state['qa']
            result = qa.invoke(f"What does Article {article_number} of the Indian Constitution state? Explain in detail.")
            
            st.markdown("<div class='article-result'>", unsafe_allow_html=True)
            st.markdown(result['result'])
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_constitutional_bodies():
    """Display information about constitutional bodies"""
    st.markdown("""
    <div class='flag-colors'>
        <div class='saffron'></div>
        <div class='white'></div>
        <div class='green'></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("## Constitutional Bodies")
    st.markdown("These are bodies that are explicitly mentioned in the Constitution of India and derive their powers and authorities directly from it.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Constitutional bodies data
    bodies = [
        {
            "name": "Election Commission of India",
            "articles": "Article 324", 
            "description": "Conducts elections to the Parliament, State Legislatures, and offices of President and Vice-President"
        },
        {
            "name": "Union Public Service Commission",
            "articles": "Articles 315-323", 
            "description": "Conducts examinations for appointments to the All-India Services and Central Services"
        },
        {
            "name": "State Public Service Commissions",
            "articles": "Articles 315-323", 
            "description": "Conducts examinations for appointments to the State Services"
        },
        {
            "name": "Comptroller and Auditor General of India",
            "articles": "Articles 148-151", 
            "description": "Audits the accounts of the Union and State Governments"
        },
        {
            "name": "Finance Commission",
            "articles": "Articles 280-281", 
            "description": "Recommends distribution of tax revenues between the Union and the States"
        },
        {
            "name": "National Commission for SCs",
            "articles": "Article 338", 
            "description": "Monitors safeguards provided for Scheduled Castes"
        },
        {
            "name": "National Commission for STs",
            "articles": "Article 338A", 
            "description": "Monitors safeguards provided for Scheduled Tribes"
        },
        {
            "name": "Attorney General of India",
            "articles": "Article 76", 
            "description": "Chief legal advisor to the Government of India"
        }
    ]
    
    # Display bodies
    for body in bodies:
        st.markdown(
            f"""
            <div class='part-card'>
                <h3>{body['name']}</h3>
                <p><strong>Constitutional Provision:</strong> {body['articles']}</p>
                <p>{body['description']}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Interactive exploration
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### Explore a Constitutional Body")
    
    selected_body = st.selectbox(
        "Select a body to explore:",
        [body['name'] for body in bodies]
    )
    
    if st.button("Get Detailed Information"):
        with st.spinner(f"Fetching information about {selected_body}..."):
            qa = st.session_state['qa']
            result = qa.invoke(f"Explain the powers, functions, and constitutional provisions related to {selected_body} in detail")
            
            st.markdown("<div class='article-result'>", unsafe_allow_html=True)
            st.markdown(result['result'])
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_amendments():
    """Display information about important constitutional amendments"""
    st.markdown("""
    <div class='flag-colors'>
        <div class='saffron'></div>
        <div class='white'></div>
        <div class='green'></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("## Important Constitutional Amendments")
    st.markdown("The Constitution of India can be amended through Article 368. Since its enactment, it has been amended over 100 times.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Important amendments data
    amendments = [
        {"number": "1st", "year": "1951", "description": "Added Ninth Schedule to protect land reform laws"},
        {"number": "7th", "year": "1956", "description": "Reorganized states on linguistic basis"},
        {"number": "42nd", "year": "1976", "description": "Added 'socialist', 'secular', and inserted Fundamental Duties"},
        {"number": "44th", "year": "1978", "description": "Restored right to property as a legal right"},
        {"number": "52nd", "year": "1985", "description": "Added Tenth Schedule containing anti-defection provisions"},
        {"number": "73rd", "year": "1992", "description": "Established Panchayati Raj institutions"},
        {"number": "74th", "year": "1992", "description": "Established municipalities"},
        {"number": "86th", "year": "2002", "description": "Made education a fundamental right for children aged 6-14"},
        {"number": "101st", "year": "2016", "description": "Introduced Goods and Services Tax (GST)"},
        {"number": "103rd", "year": "2019", "description": "Provided 10% reservation for Economically Weaker Sections"}
    ]
    
    # Display amendments in a timeline format
    st.markdown("<div class='timeline'>", unsafe_allow_html=True)
    
    for i, amendment in enumerate(amendments):
        position = "left" if i % 2 == 0 else "right"
        st.markdown(
            f"""
            <div class='amendment-card {position}'>
                <div class='amendment-content'>
                    <h3>{amendment['number']} Amendment ({amendment['year']})</h3>
                    <p>{amendment['description']}</p>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Interactive exploration
    st.markdown("<div class='content-card' style='margin-top: 30px;'>", unsafe_allow_html=True)
    st.markdown("### Explore a Specific Amendment")
    
    amendment_number = st.number_input("Enter Amendment Number", min_value=1, max_value=106, value=42)
    
    if st.button("Get Amendment Details"):
        with st.spinner(f"Fetching information about the {amendment_number}{'st' if amendment_number % 10 == 1 and amendment_number != 11 else 'nd' if amendment_number % 10 == 2 and amendment_number != 12 else 'rd' if amendment_number % 10 == 3 and amendment_number != 13 else 'th'} Amendment..."):
            qa = st.session_state['qa']
            result = qa.invoke(f"What were the key provisions and significance of the {amendment_number}{'st' if amendment_number % 10 == 1 and amendment_number != 11 else 'nd' if amendment_number % 10 == 2 and amendment_number != 12 else 'rd' if amendment_number % 10 == 3 and amendment_number != 13 else 'th'} Amendment to the Indian Constitution?")
            
            st.markdown("<div class='article-result'>", unsafe_allow_html=True)
            st.markdown(result['result'])
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def search_by_article():
    """Search and display information about specific articles"""
    st.markdown("""
    <div class='flag-colors'>
        <div class='saffron'></div>
        <div class='white'></div>
        <div class='green'></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("## Search by Article Number")
    st.markdown("Explore specific articles of the Indian Constitution.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Article search
    col1, col2 = st.columns([3, 1])
    
    with col1:
        article_number = st.number_input("Enter Article Number", min_value=1, max_value=395, value=21)
    
    with col2:
        search_button = st.button("Search Article", use_container_width=True)
    
    if search_button:
        with st.spinner(f"Fetching information about Article {article_number}..."):
            qa = st.session_state['qa']
            result = qa.invoke(f"What does Article {article_number} of the Indian Constitution state? Explain in detail.")
            
            st.markdown("<div class='article-result'>", unsafe_allow_html=True)
            st.markdown(f"## Article {article_number}")
            st.markdown(result['result'])
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Popular articles
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### Popular Articles")
    
    popular_articles = [
        {"number": 14, "title": "Equality before law"},
        {"number": 19, "title": "Protection of certain rights regarding freedom of speech, etc."},
        {"number": 21, "title": "Protection of life and personal liberty"},
        {"number": 32, "title": "Remedies for enforcement of rights conferred by this Part"},
        {"number": 352, "title": "Proclamation of Emergency"},
        {"number": 368, "title": "Power of Parliament to amend the Constitution and procedure therefor"}
    ]
    
    # Display popular articles
    cols = st.columns(3)
    for i, article in enumerate(popular_articles):
        with cols[i % 3]:
            if st.button(f"Article {article['number']}: {article['title']}", key=f"popular_{article['number']}"):
                with st.spinner(f"Fetching information about Article {article['number']}..."):
                    qa = st.session_state['qa']
                    result = qa.invoke(f"What does Article {article['number']} of the Indian Constitution state? Explain in detail.")
                    
                    st.markdown("<div class='article-result'>", unsafe_allow_html=True)
                    st.markdown(f"## Article {article['number']}: {article['title']}")
                    st.markdown(result['result'])
                    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Advanced search
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    st.markdown("## Advanced Search")
    st.markdown("Search for specific constitutional topics, articles, or keywords.")

    search_query = st.text_input("Enter your search term:", placeholder="e.g. fundamental rights, amendments, etc.")
    search_button = st.button("Search", key="advanced_search")

    if search_button and search_query:
        with st.spinner(f"Searching for '{search_query}'..."):
            qa = st.session_state['qa']
            search_result = qa.invoke(f"Search the Indian Constitution for information about: {search_query}. Provide relevant articles, interpretations, and historical context.")
            
            st.markdown("### Search Results")
            st.markdown(search_result['result'])

    # Filters section
    st.markdown("## Filter Articles")
    col1, col2 = st.columns(2)

    with col1:
        categories = ["All", "Fundamental Rights", "Directive Principles", "Citizenship", "Emergency Provisions", "Amendment Process"]
        selected_category = st.selectbox("Filter by Category:", categories)

    with col2:
        parts = ["All"] + [f"Part {roman_numeral}" for roman_numeral in ["I", "II", "III", "IV", "IVA", "V", "VI", "VII", "VIII", "IX", "IXA", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]]
        selected_part = st.selectbox("Filter by Part:", parts)

    filter_button = st.button("Apply Filters", key="filter_articles")

    if filter_button:
        with st.spinner("Filtering articles..."):
            filter_query = f"List articles from the Indian Constitution"
            
            if selected_category != "All":
                filter_query += f" related to {selected_category}"
            
            if selected_part != "All":
                filter_query += f" in {selected_part}"
                
            qa = st.session_state['qa']
            filter_result = qa.invoke(filter_query)
            
            st.markdown("### Filtered Articles")
            st.markdown(filter_result['result'])

    # Comparison feature
    st.markdown("## Compare Articles")
    st.markdown("Compare two articles to understand their relationship and differences.")

    col1, col2 = st.columns(2)

    with col1:
        first_article = st.text_input("First Article Number:", placeholder="e.g. 14")

    with col2:
        second_article = st.text_input("Second Article Number:", placeholder="e.g. 21")

    compare_button = st.button("Compare", key="compare_articles")

    if compare_button and first_article and second_article:
        with st.spinner(f"Comparing Article {first_article} and Article {second_article}..."):
            qa = st.session_state['qa']
            comparison_result = qa.invoke(f"Compare Article {first_article} and Article {second_article} of the Indian Constitution. Explain their provisions, interpretations, and relationship to each other.")
            
            st.markdown("### Comparison Results")
            st.markdown(comparison_result['result'])

    # Constitution timeline/history section
    st.markdown("## Constitutional Timeline")
    st.markdown("Explore the history and major amendments to the Indian Constitution.")

    timeline_button = st.button("Show Constitutional Timeline", key="timeline")

    if timeline_button:
        with st.spinner("Generating constitutional timeline..."):
            qa = st.session_state['qa']
            timeline_result = qa.invoke("Provide a timeline of major events and amendments in the history of the Indian Constitution from its adoption to present day.")
            
            st.markdown("### Constitutional History")
            st.markdown(timeline_result['result'])

    # Expert insights section
    st.markdown("## Expert Insights")
    st.markdown("Get detailed analysis on constitutional topics from experts.")

    expert_topics = ["Federalism", "Secularism", "Judicial Review", "Parliamentary System", "Fundamental Rights vs Directive Principles"]
    selected_topic = st.selectbox("Select a topic for expert analysis:", expert_topics)

    expert_button = st.button("Get Expert Analysis", key="expert_insights")

    if expert_button:
        with st.spinner(f"Generating expert analysis on {selected_topic}..."):
            qa = st.session_state['qa']
            expert_result = qa.invoke(f"Provide an expert analysis on {selected_topic} in the Indian Constitution. Include historical development, interpretations by courts, and modern relevance.")
            
            st.markdown(f"### Expert Analysis: {selected_topic}")
            st.markdown(expert_result['result'])

    # Add a footer
    st.markdown("---")
    st.markdown("© 2025 Indian Constitution Explorer | This application is for educational purposes only.")

if __name__ == "__main__":
    app()