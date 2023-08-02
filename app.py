import uvicorn ##ASGI
from fastapi import FastAPI, Body
from transformers import BertForSequenceClassification
from transformers import BertTokenizer
from routers.routers import router
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost",
    "http://localhost:3000",  # Update with your React app's URL
 
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, tags=["bff"])

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=9000, reload=True)
    
#uvicorn app.main:app --reload
