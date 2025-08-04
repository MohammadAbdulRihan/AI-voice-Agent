# AI VA - Python Backend Demo

A simple Flask backend application with HTML/JavaScript frontend demonstrating basic web server functionality.

## Project Structure

```AI VA/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   └── index.html     # Main page
└── static/            # Static files (CSS, JS, images)
    └── script.js      # Frontend JavaScript
```

## Features

- **Flask Backend**: Python web server with API endpoints
- **HTML Frontend**: Responsive web interface
- **JavaScript**: Interactive frontend functionality
- **API Endpoints**:
  - `/` - Main page
  - `/api/hello` - Simple greeting endpoint
  - `/api/data` - Sample users data endpoint

## Setup Instructions

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask server**:
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

- Click "Get Hello Message" to test the basic API endpoint
- Click "Load Users Data" to fetch and display sample user data
- Click "Clear Response" to clear the displayed content

## Development

The Flask server runs in debug mode, so any changes to the Python code will automatically reload the server.

## API Endpoints

### GET /api/hello
Returns a simple greeting message.

**Response:**
```json
{
  "message": "Hello from Flask backend!",
  "status": "success"
}
```

### GET /api/data
Returns sample user data.

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "total": 3
}
```
