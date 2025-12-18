# DocuQuery - RAG System

A production-ready **Retrieval-Augmented Generation (RAG)** system that enables users to upload documents and query them using natural language. Built with Python, LangChain, FAISS, Flask, and OpenAI GPT-4.

## Features

- 📄 **Multi-format Document Support**: Upload PDF, DOCX, and TXT files
- 🔍 **Semantic Search**: FAISS-powered vector similarity search
- 🤖 **AI-Powered Answers**: Context-aware responses using GPT-4
- 💾 **Metadata Storage**: MongoDB for document tracking
- 🚀 **REST API**: Clean endpoints for integration
- ⚡ **Optimized Performance**: Response latency < 2 seconds

## Architecture

```
User → Flask API → Document Processor → Text Chunker → OpenAI Embeddings → FAISS Vector Store
                ↓                                                                    ↓
            MongoDB (Metadata)                                              Similarity Search
                                                                                    ↓
                                                                            GPT-4 LLM → Answer
```

## Installation

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pythonProject
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key
   MONGODB_URI=mongodb://localhost:27017/docuquery
   ```

5. **Start MongoDB** (if running locally)
   ```bash
   mongod
   ```

## Usage

### Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "vector_store_size": 150,
  "document_count": 5
}
```

#### 2. Upload Document
```bash
POST /api/upload
Content-Type: multipart/form-data

file: <your-document.pdf>
```

**Response:**
```json
{
  "document_id": "uuid-here",
  "filename": "document.pdf",
  "chunk_count": 25,
  "status": "processed",
  "message": "Document uploaded and processed successfully"
}
```

#### 3. Query Documents
```bash
POST /api/query
Content-Type: application/json

{
  "query": "What is the main topic of the document?",
  "top_k": 3
}
```

**Response:**
```json
{
  "query": "What is the main topic of the document?",
  "answer": "Based on the provided documents, the main topic is...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk_index": 5,
      "text_preview": "...",
      "similarity_score": 0.85
    }
  ],
  "confidence": 0.9,
  "chunks_retrieved": 3
}
```

#### 4. List Documents
```bash
GET /api/documents
```

**Response:**
```json
{
  "documents": [
    {
      "document_id": "uuid-here",
      "filename": "document.pdf",
      "chunk_count": 25,
      "upload_time": "2025-12-18T05:30:00Z",
      "status": "processed"
    }
  ],
  "count": 1
}
```

#### 5. Delete Document
```bash
DELETE /api/documents/<document_id>
```

**Response:**
```json
{
  "message": "Document deleted successfully",
  "document_id": "uuid-here",
  "note": "Vector embeddings persist in FAISS index"
}
```

## Project Structure

```
pythonProject/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── utils/
│   ├── __init__.py
│   ├── document_processor.py  # Document text extraction
│   ├── text_chunker.py        # Text chunking logic
│   ├── vector_store.py        # FAISS vector operations
│   └── llm_handler.py         # LLM integration
├── database/
│   ├── __init__.py
│   └── mongodb_handler.py     # MongoDB operations
├── uploads/                   # Uploaded documents (auto-created)
└── vector_store/              # FAISS indices (auto-created)
```

## Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/docuquery` |
| `CHUNK_SIZE` | Text chunk size | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `TOP_K_RESULTS` | Number of results to retrieve | 3 |
| `LLM_TEMPERATURE` | LLM creativity (0-1) | 0.7 |

## Testing

### Using cURL

**Upload a document:**
```bash
curl -X POST -F "file=@sample.pdf" http://localhost:5000/api/upload
```

**Query the system:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}' \
  http://localhost:5000/api/query
```

### Using Python

```python
import requests

# Upload document
with open('sample.pdf', 'rb') as f:
    response = requests.post('http://localhost:5000/api/upload', files={'file': f})
    print(response.json())

# Query
response = requests.post('http://localhost:5000/api/query', 
    json={'query': 'What is the main topic?'})
print(response.json())
```

## Technologies

- **Flask**: Web framework
- **LangChain**: RAG orchestration
- **FAISS**: Vector similarity search
- **OpenAI**: Embeddings (text-embedding-3-small) & LLM (GPT-4)
- **MongoDB**: Document metadata storage
- **PyPDF2**: PDF processing
- **python-docx**: Word document processing

## Performance Optimization

- **Vector Store Persistence**: FAISS index saved to disk
- **Connection Pooling**: MongoDB connection reuse
- **Efficient Chunking**: Optimized chunk size for context/speed balance
- **Caching**: Embedding caching for repeated queries

## Limitations

- Maximum file size: 16MB
- Supported formats: PDF, DOCX, TXT
- Vector store deletion requires manual rebuild
- Requires active internet connection for OpenAI API

## Troubleshooting

**MongoDB Connection Error:**
```bash
# Ensure MongoDB is running
mongod --dbpath /path/to/data
```

**OpenAI API Error:**
- Verify API key in `.env`
- Check API quota and billing

**Import Errors:**
```bash
pip install -r requirements.txt --upgrade
```

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Author

Built with ❤️ using Python, LangChain, and OpenAI
