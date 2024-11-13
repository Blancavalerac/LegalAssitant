AI Legal Assistant Chatbot
This repository contains code for an AI-powered legal assistant chatbot, built with Streamlit, OpenAI’s GPT models, and Azure. The chatbot enables users to upload legal documents, ask questions about them, and receive straightforward answers in accessible language. The assistant uses document embeddings to retrieve relevant sections from uploaded documents, and GPT-4 to generate responses that clarify complex legal language.

Table of Contents
Features
Setup and Installation
Environment Variables
File Structure
Usage
Contributing
License
Features
Document Upload: Supports PDF document uploads and parses text for AI analysis.
Legal Assistance: Provides simplified explanations for legal clauses and concepts in a user-friendly format.
Contextual Responses: Uses embeddings to retrieve document context and focuses answers on the user's questions.
Interactive Chat Interface: Built with Streamlit, allowing a rich chat experience with user avatars and feedback.
Feedback Mechanism: Includes a feedback feature to refine answers based on user input.
Configurable Model Parameters: Supports temperature adjustment for model creativity and allows model selection.
Setup and Installation
Prerequisites
Python 3.7 or higher
Azure account with OpenAI and Blob Storage access
Neo4j Database (optional, depending on project requirements)
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/legal-assistant-chatbot.git
cd legal-assistant-chatbot
Create a virtual environment (optional but recommended):

bash
Copy code
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Load environment variables:

Set environment variables in a .env file (see Environment Variables section).

Environment Variables
Create a .env file in the root directory with the following variables:

plaintext
Copy code
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-azure-openai-endpoint.com
AZURE_BLOB_CONNECTION_STRING=your_azure_blob_connection_string
File Structure
main.py: The main application file.
requirements.txt: Contains all necessary Python libraries.
.env: Environment variables for Azure OpenAI and Blob Storage credentials.
assets/: Folder for any additional assets, such as logos or images used in the Streamlit interface.
Usage
To run the chatbot, execute the following command:

bash
Copy code
streamlit run main.py
Main Features
Chat Interface:

Users can ask questions through a chat input at the bottom of the screen.
Each question is saved in the session, and previous conversations are stored to enable context retention.
Document Upload:

Users can upload PDF documents in the sidebar, which the chatbot will process and use to extract relevant sections for responses.
The bot reads each page, extracts text, and indexes it for similarity search.
Feedback:

A feedback button allows users to submit input on the quality of the answers, enabling iterative improvements to responses.
Configurable Settings:

Temperature and model options let users adjust the output tone and select between available OpenAI models (e.g., gpt-3.5-turbo, gpt-4).
Example Workflow
Upload a Document:

Go to the 'Document Uploader' section in the sidebar and select a PDF file to upload.
The document will be processed, with each page indexed for quick access by the assistant.
Ask Questions:

Type a legal question or request for clarification in the chat input.
The chatbot responds by simplifying the legal terms in the document, referencing specific clauses where possible.
Adjust Model Parameters (optional):

In the sidebar, users can adjust the model temperature (0.0 to 2.0) and select from available models.
Provide Feedback:

After receiving a response, users can provide feedback to improve future interactions.
Code Overview
Core Sections
Streamlit UI Configuration: Sets up the page layout, header, and sidebar components, including file upload, input fields, and chat history.

Document Upload and Parsing: Processes uploaded PDF files, extracts text from each page, and prepares it for document embedding and retrieval.

Embedding Creation: Uses Azure OpenAI Embeddings with FAISS to create searchable embeddings for each document.

OpenAI Response Generation: Sends user input and context from documents to OpenAI’s GPT-4 model, which returns a response aimed at simplifying complex legal terms.

Feedback Handling: Captures user feedback for each response and displays a toast confirmation.

Key Functions
on_clear(): Clears the session state to start a new chat.
home(): Resets the sidebar to the initial state.
handle_feedback(): Records and processes user feedback for each answer.
get_avatar(role): Returns an appropriate avatar icon for each user role (user or assistant).
similarity_search(): Searches document embeddings for relevant text based on user input.
