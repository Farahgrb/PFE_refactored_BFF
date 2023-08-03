from aiohttp import ClientSession, FormData
import arabic_reshaper
import tempfile
import requests
import json
from typing import Optional, Generic,TypeVar
from pydantic import BaseModel
from bidi.algorithm import get_display
from pydantic.generics import GenericModel
from fastapi import  HTTPException
from aiohttp import ClientSession, ClientTimeout



class id_text(BaseModel):
    id:Optional[str]=None 

T = TypeVar("T")

class Response(GenericModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]

async def file_to_data(payload_obj) -> FormData:

    temp = tempfile.NamedTemporaryFile(mode="w+b", delete=False)
    temp.name = payload_obj.filename
    data = FormData()
    try:
        temp.writelines(payload_obj.file)
        temp.seek(0)
        data.add_field('wav', temp.read(), filename=payload_obj.filename)
        temp.close()
    except Exception as exception:
      print("hi")
    return data

async def transcribe_audio(file, asr_microservice_url, classification_microservice_url):
    try:
        timeout = ClientTimeout(total=600)  
        async with ClientSession(timeout=timeout) as session:
            # Transcribe the audio file using ASR microservice
            async with session.post(
                url=f"{asr_microservice_url}/transcription",
                data=await file_to_data(file),
            ) as response:
                response.raise_for_status()
                transcription = await response.json()
                reshaped_text = arabic_reshaper.reshape(transcription.get("Transcription"))

            # Classify the transcribed text using the classification microservice
            async with session.post(
                url=f"{classification_microservice_url}/detection/classification/creation",
                json={"text": reshaped_text},
            ) as response1:
                response1.raise_for_status()
                data = await response1.json()  # This will parse the response data as JSON

        return data

    except Exception as e:
        return {"error": str(e)}
    
async def upload_file(file):
    try:
            # Save the uploaded file to a desired location
        with open(file.filename, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Return a response indicating the successful upload
        return {"message": "File uploaded successfully"}
    except requests.exceptions.RequestException as e:
        # Handle errors from the classification microservice
        print("Error: ", e)
        return None

async def text_classify(text_input,classification_microservice_url):
    try:
    
    # text_input = await request.json()
    
        response = requests.post(f"{classification_microservice_url}/detection/classification/creation", json=text_input)
        response.raise_for_status()
      
        result = response.text
        print(result)

        api_response_dict = json.loads(result)
        
        return api_response_dict
    except requests.exceptions.RequestException as e:
    # Handle errors from the classification microservice
        print("Error: ", e)
        return None
    
def delete_row(request:id_text, classification_microservice_url):
    try:
        response = requests.delete(f"{classification_microservice_url}/detection/deletion", json=request.dict())
        response.raise_for_status()
        return Response(status="Ok", code="200", message="Success delete data").dict(exclude_none=True)

    except requests.exceptions.RequestException as e:
    # Handle errors from the classification microservice
        print("Error: ", e)
        return None
    
async def update_detection(request:dict, classification_microservice_url):
    try:
        response = requests.patch(f"{classification_microservice_url}/detection/label/update", json=request)
        response.raise_for_status()
        return Response(status="Ok", code="200", message="Success delete data").dict(exclude_none=True)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error communicating with the microservice")

def rows(classification_microservice_url):
    response = requests.get(f"{classification_microservice_url}/detection/all/data")

    # Check if the request was successful (status code 200)
    try:
        db_response = response.json()  # Assuming the response is in JSON format
       
        return db_response
    except requests.exceptions.RequestException as e:
        return e