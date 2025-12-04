# PDF Chatbot API

## Upload PDF
**POST /upload**
- Headers: `user-id: string`
- Body: form-data with key `file`
- Response: JSON with upload status

## Chatbot
**POST /chatbot**
- Headers: `user-id: string`
- Body: JSON `{ "question": "your question" }`
- Response: JSON `{ "question": "...", "answer": "...", "user_id": "..." }`
