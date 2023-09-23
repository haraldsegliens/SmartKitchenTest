import json
import os
import sys

from typing import Annotated

import aiofiles
import asyncio
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from flaskwebgui import FlaskUI
from starlette.responses import FileResponse

from hardcoded_data import form_storage, pattern_match_config
from word_pattern_match import pattern_match


async def transcribe_audio(audio_path, task="transcribe", return_timestamps=False):
    """Function to transcribe an audio file using our endpoint"""
    import gradio_client

    api_url = "sanchit-gandhi/whisper-jax"
    client = gradio_client.Client(api_url)

    text, runtime = client.predict(
        audio_path,
        task,
        return_timestamps,
        api_name="/predict_1",
    )

    return text


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


app = FastAPI()


@app.get("/")
async def read_index_html():
    return FileResponse(resource_path('html/index.html'))


@app.get("/forms")
async def read_forms_html():
    return FileResponse(resource_path('html/forms.html'))


@app.get("/data/forms")
async def read_forms_list():
    return [form.name for form in form_storage.forms]


@app.get("/data/forms/{form_index}")
async def read_forms_data(form_index: int):
    if form_index >= len(form_storage.forms):
        raise HTTPException(status_code=400, detail="Form with index " + str(form_index) + " not found!")

    form = form_storage.forms[form_index]
    return {
        "columns": form.get_form_columns(),
        "records": json.loads(form.data_frame.to_json(orient="records"))
    }


@app.post("/process-recording")
async def process_recording(file: UploadFile = File(...)):
    async with aiofiles.open("test.wav", 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    output = await asyncio.wait_for(transcribe_audio("test.wav"), timeout=20)

    pattern_match_response = pattern_match(pattern_match_config, output)

    if pattern_match_response is not None:
        form_storage.input_pattern_matches(pattern_match_response)

    response = {
        "text": output,
        "matches": pattern_match_response
    }
    print(response)
    return response


# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=3000)

if __name__ == "__main__":
   FlaskUI(app=app, server="fastapi", fullscreen=False, width=1000, height=1000).run()
