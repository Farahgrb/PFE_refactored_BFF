from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Generic,TypeVar
from fastapi.middleware.cors import CORSMiddleware
from pydantic.generics import GenericModel
import os
from services.services import transcribe_audio, upload_file, text_classify, delete_row, update_detection, rows
from dotenv import dotenv_values
env_vars = dotenv_values()

router = APIRouter()


class id_text(BaseModel):
    id:Optional[str]=None
T = TypeVar("T")
class Response(GenericModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]






asr_microservice_url = env_vars["ASR_MICROSERVICE_URL"]
classification_microservice_url = env_vars["CLASSIFICATION_MICROSERVICE_URL"]

@router.get('/')
async def Home():
    return "welcome from BFF"

@router.post("/audio/hate/classification") #audio/hate/classification/transcribe
async def transcribe(file: UploadFile = File(...), device: str = "cpu"):
    result = await transcribe_audio(file, asr_microservice_url, classification_microservice_url)
    return result



@router.post("/file/upload") #/file-upload
async def file_upload(file: UploadFile):
    return upload_file(file)

@router.post('/text/classification') #classifytext
async def classify_text(text_input: dict):
    return await text_classify(text_input,classification_microservice_url)

@router.delete('/classification/deletion') #/delete'
async def delete_roww(request:id_text):
    return  delete_row(request,classification_microservice_url)

@router.patch("/classification/update")#/update
async def update_detection_bff(request: dict):
    return await update_detection(request,classification_microservice_url)

@router.get("/classification/fetching")#fetsh
async def get_rows():
    return rows(classification_microservice_url)