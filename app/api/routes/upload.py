from fastapi import APIRouter, File, UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from scripts.codeGeneration import code_generator
import os

router = APIRouter()

@router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def create_upload_file(file: UploadFile = File(...)):
    content = await file.read()
    zip_file_path = "generated_project.zip"
    max_attempts = 5

    for attempt in range(max_attempts):
        code_generator.run(content)
        if os.path.exists(zip_file_path):
            break
    else:
        raise HTTPException(status_code=500, detail="Zip folder generation failed".format(max_attempts))

    return FileResponse(path=zip_file_path, media_type="application/zip", filename="generated_project.zip")