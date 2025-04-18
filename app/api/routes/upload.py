from fastapi import APIRouter, File, UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from scripts.codeGenerationPipeline import code_generator
import os
from config.config import settings

router = APIRouter()

@router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    file_content = await file.read()
    for attempt in range(settings.MAX_ATTEMPS):
        code_generator.run_pipeline(file_content)
        if os.path.exists(settings.GENERATED_PROJECT_ZIP_NAME):
            break
    else:
        raise HTTPException(status_code= 500, detail="Zip folder generation failed".format(settings.MAX_ATTEMPS))
    
    return FileResponse(path=settings.GENERATED_PROJECT_ZIP_NAME, media_type="application/zip", filename=settings.GENERATED_PROJECT_ZIP_NAME)