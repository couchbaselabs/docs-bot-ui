# Docs ChatBot UI

A Streamlit-based user interface for the Docs ChatBot application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your Docs ChatBot API is running on `http://localhost:8000`

2. Start the Streamlit application:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

## Features

- Clean and intuitive chat interface
- Real-time chat history
- API status monitoring
- Responsive design
- Error handling for API communication

## API Integration

The application expects the following API endpoints to be available:
- `POST /chat` - Send chat messages and receive responses
- `GET /health` - Check API health status

Make sure your API is running and accessible at `http://localhost:8000` before starting the Streamlit application. 