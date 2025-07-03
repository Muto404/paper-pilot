import uvicorn
import os
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_processor import extract_text_from_pdf
from vector_store import VectorStore
from qa_service import get_answer_from_llm

app = FastAPI(
    title="Paper Pilot API",
    description="API for parsing and analyzing academic papers.",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Paper(BaseModel):
    id: str

class AskRequest(BaseModel):
    question: str

@app.post("/api/v1/papers", response_model=Paper, tags=["Papers"])
async def upload_paper(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is supported.")
    
    paper_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{paper_id}.pdf")

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        text = extract_text_from_pdf(file_path)
        VectorStore(paper_id, text)
    finally:
        os.remove(file_path)

    return Paper(id=paper_id)

@app.post("/api/v1/papers/{paper_id}/ask", tags=["Papers"])
async def ask_question(paper_id: str, request: AskRequest):
    retriever_data = VectorStore.get_retriever(paper_id)
    if not retriever_data:
        raise HTTPException(status_code=404, detail="Paper not found.")

    vector_db = retriever_data["vector_db"]
    model = retriever_data["model"]
    sentences = retriever_data["sentences"]
    
    query_embedding = model.encode([request.question])
    distances, indices = vector_db.search(query_embedding, k=3)
    
    context = "\n".join([sentences[i] for i in indices[0]])
    
    answer = get_answer_from_llm(request.question, context)
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


# 这是一个方便本地开发时直接运行的入口
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)