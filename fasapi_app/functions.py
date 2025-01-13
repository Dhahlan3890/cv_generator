import google.generativeai as genai
import os
import PyPDF2
import subprocess
import shutil
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text


def advanced_chat(friend_cv, pdf_path ):
  chat_session = model.start_chat(history=[])
  prompt = "i will give you the latex code of my friends cv, my details till that dont answer anything wait. after i gave you both modify my friends cv with my details."
  description = chat_session.send_message(prompt)
  description = description.text
  print("initialized")
  cv_prompt = f"Friend CV\n{friend_cv}"
  refined_description = chat_session.send_message(cv_prompt)
  refined_description = refined_description.text
  print("cv initialized")
  details = extract_text_from_pdf(pdf_path)
  detail_prompt = f"My details\n{details}"
  initial_html = chat_session.send_message(detail_prompt)
  initial_html = initial_html.text
  print("details initialized")
  
  fixing_prompt = "fix Misplaced alignment character error, Runaway argument error, Emergency stop error in your code and the corrected full code"
  refined_html = chat_session.send_message(fixing_prompt)
  refined_html = refined_html.text
  print("fixes done")
  
  character_fixing_prompt = "fix errors in characters like &"
  refined_cv = chat_session.send_message(character_fixing_prompt)
  refined_cv = refined_cv.text
  print("fixes recheck completed")

  character_fixing_prompt = "Fill the spaces with neccessary details and give FULL CODE"
  refined_cv = chat_session.send_message(character_fixing_prompt)
  refined_cv = refined_cv.text
  print("spaces filled")

  character_fixing_prompt = "Fill or remove the [] neccessary details and give FULL CODE"
  refined_cv = chat_session.send_message(character_fixing_prompt)
  refined_cv = refined_cv.text
  print("unnecessary spaces filled")

  character_fixing_prompt = "recheck for errors and fix then give full code"
  final_cv = chat_session.send_message(character_fixing_prompt)
  final_cv = final_cv.text

  return final_cv



def latex_to_pdf(latex_code, output_path):
    # Create the directory if it doesn't exist
    generated_cvs_dir = os.path.join(os.path.dirname(__file__), "generated_cvs")
    os.makedirs(generated_cvs_dir, exist_ok=True)

    frontend_public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",  "frontend", "public"))
    
    
    temp_tex_path = os.path.join(generated_cvs_dir, "temp.tex")
    with open(temp_tex_path, "w") as file:
        file.write(latex_code)
    frontend_tex_path = os.path.join(frontend_public_dir, "temp.tex")
    if os.path.exists(frontend_tex_path):
        os.remove(frontend_tex_path)
    shutil.copy(temp_tex_path, frontend_public_dir)
    print("latex file created")
    
    try:
        # Change working directory to where the temp.tex file is located
        os.chdir(generated_cvs_dir)
        
        # Run pdflatex
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'temp.tex'], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("pdf created")
        
    except subprocess.CalledProcessError as e:
        print(f"Warning: LaTeX compilation encountered an issue: {e}")
    finally:
        # Change back to the original directory
        os.chdir(os.path.dirname(os.path.dirname(__file__)))
    
    # Move the output PDF if it exists
    temp_pdf_path = os.path.join(generated_cvs_dir, "temp.pdf")
    frontend_pdf_path = os.path.join(frontend_public_dir, "temp.pdf")
    if os.path.exists(frontend_pdf_path):
        os.remove(frontend_pdf_path)
    shutil.copy(temp_pdf_path, frontend_public_dir)
    
    if os.path.exists(temp_pdf_path):
        output_pdf_path = os.path.join(generated_cvs_dir, output_path)
        os.rename(temp_pdf_path, output_pdf_path)
        print("pdf renamed")
    else:
        print("Error: PDF was not created. Please check LaTeX code for critical errors.")
    
    # Clean up temporary files
    for ext in ["aux", "log"]:
        temp_file = os.path.join(generated_cvs_dir, f"temp.{ext}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Ensure the directory exists before joining the path
# input_cv_dir = os.path.join(os.path.dirname(__file__), "input_cv")
# os.makedirs(input_cv_dir, exist_ok=True)
# path = os.path.join(input_cv_dir, "cv.pdf")

# # Check if the file exists
# if not os.path.exists(path):
#     raise FileNotFoundError(f"The CV file does not exist at {path}")

# # path = os.path.join(os.path.dirname(__file__), "cv.pdf")
# latex_code = advanced_chat(fr_cv, path)
# latex_code = latex_code.split('\\documentclass')[1]
# latex_code = '\\documentclass' + latex_code
# latex_code = latex_code.split('\\end{document}')[0] + '\\end{document}'

# output_filename = 'generated_cv.pdf'
# latex_to_pdf(latex_code, output_filename)