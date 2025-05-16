from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Importing your prebuilt agent logic 
import llm_agent

app = FastAPI()

# Using CORS (so Streamlit can talk to FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(payload: Question):
    question = payload.question
    answer = llm_agent.run_llm_agent(question)
    return {"answer": answer}
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running"}

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)
