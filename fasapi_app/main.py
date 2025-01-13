from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from functions import advanced_chat, latex_to_pdf
import logging
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://resumegeni.netlify.app"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/items")
async def read_items():
    # This is a placeholder. You can replace it with actual data from a database.
    items = [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
        {"id": 3, "name": "Item 3"},
    ]
    return items

@app.post("/api/generate-cv")
async def generate_cv(friend_cv: str = Form(...), user_cv: UploadFile = File(...)):
    try:
        logger.info(f"Received friend_cv: {friend_cv}")
        logger.info(f"Received user_cv filename: {user_cv.filename}")
        
        # Save the uploaded PDF temporarily
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        input_cv_dir = os.path.join(os.path.dirname(__file__), "input_cv")
        os.makedirs(input_cv_dir, exist_ok=True)
        temp_pdf_path = os.path.join(input_cv_dir, f"{timestamp}_{user_cv.filename}")
        with open(temp_pdf_path, "wb") as buffer:
            buffer.write(await user_cv.read())
        
        # Generate LaTeX code
        latex_code = advanced_chat(friend_cv, temp_pdf_path)
        
        # Clean up LaTeX code
        latex_code = latex_code.split('\\documentclass')[1]
        latex_code = '\\documentclass' + latex_code
        latex_code = latex_code.split('\\end{document}')[0] + '\\end{document}'
        
        # Generate PDF
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f'generated_cv_{timestamp}.pdf'
        latex_to_pdf(latex_code, output_filename)
        
        # Return the generated PDF
        generated_cvs_dir = os.path.join(os.path.dirname(__file__), "generated_cvs")
        return FileResponse(os.path.join(generated_cvs_dir, output_filename), filename=output_filename)
    except Exception as e:
        logger.error(f"Error in generate_cv: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/tex-to-pdf-file")
async def tex_to_pdf_file(tex_code: str = Form(...)):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f'temp_{timestamp}.pdf'
        latex_to_pdf(tex_code, output_filename)
        # os.remove(output_filename)
        generated_cvs_dir = os.path.join(os.path.dirname(__file__), "generated_cvs")
        return FileResponse(os.path.join(generated_cvs_dir, output_filename), filename=output_filename)
    except Exception as e:
        logger.error(f"Error in tex_to_pdf_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
