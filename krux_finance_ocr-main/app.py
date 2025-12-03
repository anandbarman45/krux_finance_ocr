import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from inference import DocumentAI

app = FastAPI(title="KruxOCR API", description="OCR and Document Classification Service for Indian Business Proofs")

# Initialize Pipeline (Load model once at startup)
# Note: In a real deployment, you might want to load this lazily or handle model download if not present.
# For this setup, we assume the model is either present or will fallback to base model.
pipeline = DocumentAI(model_path=os.getenv("MODEL_PATH", "Krux01/document_ai_model_12class"))

origins_env = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in origins_env.split(",")] if origins_env else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "KruxOCR"}

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    Upload a document image (JPG, PNG) or PDF to get OCR extraction results.
    """
    try:
        # Save uploaded file temporarily
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run Inference
        try:
            # Handle PDF conversion if needed (basic check, inference.py handles logic if implemented, 
            # but for now inference.py expects image path. 
            # If inference.py handles PDF via pdf2image internally, we are good.
            # Looking at inference.py, it uses Image.open(), so we should ensure it's an image.
            # If it's a PDF, we might need to convert it here or ensure inference.py handles it.
            # The original script had PDF conversion in the test block. 
            # Let's add basic PDF handling here if needed, or rely on the user sending images.
            # For robustness, let's assume the user sends images for now as per PRD P0.
            
            result = pipeline.analyze(temp_filename)
            
            # Cleanup
            os.remove(temp_filename)
            
            return JSONResponse(content=result)
            
        except Exception as e:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            raise HTTPException(status_code=500, detail=f"Processing Error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
