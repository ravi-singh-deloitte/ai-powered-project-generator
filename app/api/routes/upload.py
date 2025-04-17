from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse

from scripts.codeGeneration import code_generator

router = APIRouter()

@router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def create_upload_file(file: UploadFile = File(...)):
    content = await file.read()
    output = code_generator.extract_text_from_docx(content)
    print(output)
    print({"filename": file.filename, "content_type": file.content_type})
    return JSONResponse(content={"filename": file.filename, "content_type": file.content_type})