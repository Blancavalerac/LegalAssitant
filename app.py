import os
import sys
import time
import json
import warnings
import faiss

import openai
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from neo4j import GraphDatabase

import streamlit as st
from streamlit_chat import message
from streamlit_extras.tags import tagger_component
from streamlit_extras.bottom_container import bottom
from streamlit_option_menu import option_menu
from streamlit_feedback import streamlit_feedback
from streamlit_pdf_viewer import pdf_viewer


from langchain.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS as CommunityFAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


load_dotenv()


# Set up credentials and initial configuration
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

model_index = "text-embedding-ada-002"
embedding = AzureOpenAIEmbeddings(model="text-embedding-ada-002")


# Initialize Streamlit variables

if 'embeddings' not in st.session_state:
    st.session_state.embeddings = {}

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'names' not in st.session_state:
    st.session_state.names = []

if 'user_input' not in st.session_state:
    st.session_state.user_input = ''


# Function to clear session state variables for a new chat
def on_clear():
    st.session_state.user_input = ''
    st.session_state.db_kyc = None
    st.session_state.messages = []
    
# Function to set home screen state
def home():
    st.session_state.sub_item_clicked = False
    
# Function to handle feedback input
def handle_feedback():  
    st.write(st.session_state.fbk)
    st.toast("✔️ Feedback received!")

# Function to get the correct avatar icon based on user role
def get_avatar(role):
    if role == "assistant":
        icon = "🧠"
    if role == "user":
        icon = "👤"
    return icon


# Streamlit page configuration
st.set_page_config(
    page_title="AI Legal Assistant",
    page_icon="💬",
    layout="wide"
)

# Style to hide the Streamlit menu
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
"""

# Function to handle 'New Chat' button click
def on_click():
    st.session_state.user_input = ""


# Main content based on sidebar selection
st.markdown('''
    <span style="font-size: 3vw; color: #0C1B3DF;">AI Legal Assistant</span>
''', unsafe_allow_html=True)


# Set up predetermined messages
predetermined_messages = [{"role": "assistant", "content": '''
Welcome to our Legal Language Chatbot! This tool allows you to upload any legal document and get clear, straightforward answers to your questions. Our chatbot is designed to simplify complex legal language, making it easier for anyone—regardless of legal expertise—to understand.  '''}]

if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = predetermined_messages.copy()



# Chat and messages section

with st.expander('Document Uploader'):
    if 'pdf_ref' not in st.session_state:
        st.session_state.pdf_ref = None
        
    # PDF file upload
    pdf_ref = st.file_uploader("Upload your files", type=('pdf'), key='pdf_kyc', accept_multiple_files=True)
    
    # Process each uploaded PDF
    try:
        names = []
        for pdfs in pdf_ref:
            name_doc = pdfs.name
            names.append(name_doc)
    except:
        names = []

    if st.session_state.pdf_kyc:
        st.session_state.pdf_ref = st.session_state.pdf_kyc

    # Check if new PDFs are uploaded
    if st.session_state.pdf_ref and pdf_ref is not None and names != st.session_state.names:
        st.session_state.names = []
        for pdfs in pdf_ref:
            name_doc = pdfs.name
            with st.spinner(f'Loading the document **{name_doc}**...'):
                st.session_state.names.append(name_doc)
                
                # Read text from each page of the PDF and create Document objects
                text = []
                pdfs = PdfReader(pdfs)
                total_pages = len(pdfs.pages)
                
                for page_number in range(total_pages):
                    page = pdfs.pages[page_number]
                    text.append(Document(page_content=page.extract_text(), metadata=dict(source=name_doc, page=page_number + 1)))

            # Display success message once the document is processed
            with st.spinner('Making the document readable for **AI Legal Assistant**...'):
                faiss_index = FAISS.from_documents(text, embedding)
                st.session_state.db_kyc = faiss_index
                st.write(f'**{name_doc}** uploaded :heavy_check_mark:')
                st.toast(f':heavy_check_mark: {name_doc} successfully uploaded')
                                    

# Display chat messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=get_avatar(message["role"])):
        st.markdown(message["content"])

# Limit message list to last two entries to manage memory
message_list = st.session_state.messages[1:]
if len(message_list) > 1:
    message_list = message_list[-2:]
    
# Input area at the bottom of the screen
with bottom():     
    col1, col2 = st.columns([1, 10]) 

    with col1.popover('New Chat'):
        tab1_pop, tab2_pop = st.tabs(['Actions', 'Configuration'])
        with tab1_pop:
            # Button to clear conversation
            clear_button = st.button("Clear conversation", key="clear_2", on_click=on_clear)
        with tab2_pop:
            # Settings for automatic skill detection and model selection
            auto_skill = st.toggle('Automatic capability detector', True)
            model = st.selectbox('Select model', ['gpt-35-turbo', 'gpt-4'], 1)
            temperature = st.slider('Temperature', 0.0, 2.0, 0.3, 0.1, help='''Values between 0 and 2. 
                \nHigher the value the more random the output.''')

    prompt = col2.chat_input("Insert your question")

# Handle user input and chatbot responses
if prompt:
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user input in chat
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="👤"):
        message_placeholder = st.empty()
        context_total = []
        references = []
        names_docs = set()
        
        # If PDF is uploaded, perform similarity search and retrieve context
        if st.session_state.db_kyc is not None and pdf_ref != []:
            context = st.session_state.db_kyc.similarity_search(prompt, k=10)
            context_total.append(context)
            references.append('Sources: ')
            for element in st.session_state.names:
                references.append(element)

        # Display spinner while reviewing document
        with st.spinner("Reviewing Uploaded Documentation"):
            time.sleep(1)

            # Set up the system prompt for assistant
            sistema = {"role": "system", "content": f'''
                You are a highly knowledgeable and approachable legal assistant specializing in simplifying complex legal language. Users will upload legal documents and ask questions about them. Your primary goal is to make legal concepts understandable by breaking down complex terms and providing clear, concise explanations. Use a friendly and professional tone, aiming to reduce any intimidation users may feel when interacting with legal information.

                Key Instructions:
                ...
                
                This is the document you have to review: {context_total}
                These are the previous messages of the conversation: {message_list}
            '''}

            # Prepare the assistant's messages
            messages = []
            messages.append(sistema)
            messages.append({"role": "user", "content": prompt})
        
            # Generate response using OpenAI API
            completion = client.chat.completions.create(
                model='gpt-4-32k',
                messages=messages,
                temperature=0.3,
                n=1,
                stream=True
            )

            # Stream assistant's response and display it
            response = completion
            response = message_placeholder.write_stream(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

