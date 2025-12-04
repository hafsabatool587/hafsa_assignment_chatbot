from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
from utills import load_and_process_pdf, get_user_chain
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"] if serving HTML via local server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_FOLDER = "pdf_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================================
# REQUEST MODEL
# ================================
class ChatRequest(BaseModel):
    question: str


# ================================
# UPLOAD PDF ENDPOINT
# ================================
@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Header(default=None)
):
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header is required")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files allowed")

    save_path = os.path.join(UPLOAD_FOLDER, f"{user_id}.pdf")

    # Save file
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # Build embeddings & chain
    load_and_process_pdf(user_id, save_path)

    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "message": "PDF uploaded and processed",
            "file": file.filename,
            "user_id": user_id
        }
    )


# ================================
# CHATBOT ENDPOINT
# ================================
@app.post("/chatbot")
async def chatbot_endpoint(
    request: ChatRequest,
    user_id: str = Header(default=None)
):

    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header is required")

    user_session = get_user_chain(user_id)

    if not user_session:
        raise HTTPException(
            status_code=400,
            detail="Oops! I don’t see any PDF uploaded yet. Go ahead and upload one so we can get started."
        )

    qa_chain = user_session["qa_chain"]

    try:
        response = qa_chain.invoke({"query": request.question})
        answer = response["result"]

        return {
            "user_id": user_id,
            "question": request.question,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )

@app.get("/")
async def get_frontend():
    return FileResponse("frontend/index.html")