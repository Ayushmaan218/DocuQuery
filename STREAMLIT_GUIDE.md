# Running DocuQuery with Streamlit UI

This guide shows you how to run the DocuQuery system with the beautiful Streamlit web interface.

## Prerequisites

1. **Install Streamlit** (if not already installed):
   ```bash
   pip install streamlit requests
   ```

2. **Make sure Flask API is running**:
   ```bash
   python app.py
   ```
   Keep this terminal open!

## Running the Streamlit UI

In a **new terminal** (keep Flask running in the first one):

```bash
streamlit run streamlit_app.py
```

The Streamlit app will automatically open in your browser at `http://localhost:8501`

## Features

### 📤 Upload Documents Tab
- Drag & drop or browse to upload PDF, DOCX, or TXT files
- Real-time processing status
- Automatic chunking and embedding generation
- Success metrics showing chunks created

### 💬 Ask Questions Tab
- Natural language query input
- Adjustable number of sources to retrieve (1-10)
- AI-powered answers with confidence scores
- Source citations with similarity scores
- Expandable source previews

### 📊 Sidebar Features
- **System Status**: Real-time health check
- **Document Count**: Number of uploaded documents
- **Vector Store Size**: Total chunks in the system
- **Document List**: View and manage all uploaded documents
- **Delete Documents**: Remove documents with one click

## Usage Flow

1. **Start Flask API** (Terminal 1):
   ```bash
   python app.py
   ```

2. **Start Streamlit UI** (Terminal 2):
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Upload Documents**:
   - Go to "Upload Documents" tab
   - Select a file (PDF, DOCX, or TXT)
   - Click "Upload and Process"
   - Wait for processing to complete

4. **Ask Questions**:
   - Go to "Ask Questions" tab
   - Type your question
   - Adjust number of sources if needed
   - Click "Get Answer"
   - View answer with confidence score and sources

## Tips

- **Upload multiple documents** to build a comprehensive knowledge base
- **Use specific questions** for better answers
- **Check confidence scores** - higher is better
- **Review sources** to verify answer accuracy
- **Adjust top_k** to retrieve more or fewer sources

## Troubleshooting

**"Cannot connect to API"**
- Make sure Flask is running: `python app.py`
- Check that Flask is on port 5000

**"Upload failed"**
- Check file size (max 16MB)
- Ensure file format is PDF, DOCX, or TXT
- Verify OpenAI API key is set in `.env`

**"No answer generated"**
- Upload documents first
- Make sure documents are processed successfully
- Try rephrasing your question

## Stopping the Application

1. Stop Streamlit: Press `Ctrl+C` in Terminal 2
2. Stop Flask: Press `Ctrl+C` in Terminal 1
