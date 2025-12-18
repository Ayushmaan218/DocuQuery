"""
DocuQuery Streamlit UI
A beautiful web interface for the RAG system built with Streamlit
"""

import streamlit as st
import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

# Page Configuration
st.set_page_config(
    page_title="DocuQuery - AI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    .answer-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .source-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #8b5cf6;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        📚 DocuQuery
    </h1>
    <p style='font-size: 1.2rem; color: #64748b;'>
        AI-Powered Document Question Answering System
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 System Status")
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            st.success("✅ System Online")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", health_data.get('document_count', 0))
            with col2:
                st.metric("Vectors", health_data.get('vector_store_size', 0))
        else:
            st.error("❌ API Offline")
    except:
        st.error("❌ Cannot connect to API")
        st.info("Make sure Flask server is running:\n`python app.py`")
    
    st.divider()
    
    st.header("📁 Uploaded Documents")
    
    # Fetch and display documents
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            docs = response.json().get('documents', [])
            
            if docs:
                for doc in docs:
                    with st.expander(f"📄 {doc['filename']}", expanded=False):
                        st.write(f"**Chunks:** {doc['chunk_count']}")
                        st.write(f"**Uploaded:** {doc['upload_time'][:10]}")
                        st.write(f"**Status:** {doc['status']}")
                        
                        if st.button(f"🗑️ Delete", key=f"del_{doc['document_id']}"):
                            del_response = requests.delete(
                                f"{API_BASE_URL}/documents/{doc['document_id']}"
                            )
                            if del_response.status_code == 200:
                                st.success("Document deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete")
            else:
                st.info("No documents uploaded yet")
    except:
        st.warning("Could not fetch documents")

# Main Content
tab1, tab2 = st.tabs(["📤 Upload Documents", "💬 Ask Questions"])

# Tab 1: Upload Documents
with tab1:
    st.header("Upload Your Documents")
    st.write("Upload PDF, DOCX, or TXT files to build your knowledge base")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt'],
        help="Maximum file size: 16MB"
    )
    
    if uploaded_file is not None:
        st.info(f"📄 Selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.2f} KB)")
        
        if st.button("🚀 Upload and Process", type="primary"):
            with st.spinner("Processing document... This may take a few seconds."):
                try:
                    files = {'file': uploaded_file}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    
                    if response.status_code == 201:
                        result = response.json()
                        st.success("✅ Document uploaded successfully!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Filename", result['filename'])
                        with col2:
                            st.metric("Chunks Created", result['chunk_count'])
                        with col3:
                            st.metric("Status", result['status'])
                        
                        st.balloons()
                        st.rerun()
                    else:
                        error = response.json().get('error', 'Unknown error')
                        st.error(f"❌ Upload failed: {error}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Tab 2: Ask Questions
with tab2:
    st.header("Ask Questions About Your Documents")
    st.write("Enter your question below and get AI-powered answers from your uploaded documents")
    
    # Query input
    query = st.text_area(
        "Your Question",
        placeholder="e.g., What is the main topic of the document?",
        height=100,
        help="Ask any question about your uploaded documents"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        top_k = st.slider("Number of sources to retrieve", 1, 10, 3)
    with col2:
        st.write("")  # Spacing
        ask_button = st.button("🔍 Get Answer", type="primary")
    
    if ask_button and query:
        with st.spinner("🤔 Thinking... Searching documents and generating answer..."):
            try:
                payload = {
                    "query": query,
                    "top_k": top_k
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/query",
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display Answer
                    st.markdown("### 💡 Answer")
                    st.markdown(f"""
                    <div class='answer-box'>
                        <p style='font-size: 1.1rem; line-height: 1.8; margin: 0; color: #000000;'>
                            {result['answer']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Confidence Score
                    confidence = result.get('confidence', 0)
                    if confidence >= 0.7:
                        st.success(f"🎯 Confidence: {confidence:.1%} (High)")
                    elif confidence >= 0.4:
                        st.warning(f"⚠️ Confidence: {confidence:.1%} (Medium)")
                    else:
                        st.error(f"❌ Confidence: {confidence:.1%} (Low)")
                    
                    # Sources
                    sources = result.get('sources', [])
                    if sources:
                        st.markdown("### 📚 Sources")
                        st.write(f"Retrieved {len(sources)} relevant sections:")
                        
                        for i, source in enumerate(sources, 1):
                            with st.expander(f"Source {i}: {source['filename']} (Section {source['chunk_index'] + 1})"):
                                st.write(f"**Similarity Score:** {source['similarity_score']:.4f}")
                                st.markdown(f"""
                                <div class='source-box'>
                                    <p style='font-size: 0.9rem; color: #475569;'>
                                        {source['text_preview']}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Metadata
                    with st.expander("ℹ️ Query Details"):
                        st.json({
                            "query": result['query'],
                            "chunks_retrieved": result['chunks_retrieved'],
                            "confidence": result['confidence']
                        })
                else:
                    error = response.json().get('error', 'Unknown error')
                    st.error(f"❌ Query failed: {error}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    elif ask_button:
        st.warning("⚠️ Please enter a question first")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 2rem 0;'>
    <p>Built with ❤️ using Python, LangChain, FAISS, and Streamlit</p>
    <p style='font-size: 0.9rem;'>Powered by OpenAI GPT-4 | Vector Search with FAISS</p>
</div>
""", unsafe_allow_html=True)
