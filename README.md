##  **Project Features**

### **• Upload Multiple PDF Documents**
Easily upload one or several PDF files that will be processed and indexed for question-answering.

### **• Ask Questions With Accurate, PDF-Based Answers**
The chatbot uses LLM + vector embeddings to answer strictly from the uploaded document content.

### **• Clean and Modern Chat UI**
A simple and responsive HTML/JS/CSS interface designed for smooth, user-friendly interaction.

### **• Secure API Key Management**
Environment variables are handled using a `.env` file to keep your API keys private and safe.

### **• Fully Dockerized Setup**
Run the entire application anywhere with a single command using Docker—no manual setup needed.

### **• FastAPI Backend With CORS Support**
Ensures seamless communication between frontend and backend across different origins.

### **• Modular & Scalable Code Structure**
Code is organized into clean modules for easy development, debugging, and future expansion.

##  **Installation & Setup**
### **1 Clone the Repository**
##  **Create enviroment **
1 python -m venv venv
2 venv\Scripts\activate
3 pip install -r requirements.txt
4 Create a .env file in the project root and add your keys:
5 uvicorn app.main:app --reload
6 Open index.html in your browser to start interacting with the chatbot.