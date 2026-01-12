from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from pydantic import BaseModel
from .models import Resume, Experience, Education, JobDescription
from .document_generator import generate_pdf_resume, generate_word_resume
from .openai_processor import tailor_resume 
from . import database as db
import openai
import uuid 
import os
from dotenv import dotenv_values

# Load environment variables from .env file
config = dotenv_values(".env")

# Set OpenAI API key from environment variable or .env file
os.environ["OPENAI_API_KEY"] = config.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (generated resumes)
app.mount("/static", StaticFiles(directory="backend/tmp"), name="static")

# In-memory storage for generated resumes
generated_resumes_db: Dict[str, Resume] = {}

# --- Hardcoded Base User Resume (Based on your provided information) ---
BASE_USER_RESUME = Resume(
    name="MAHIM MITTAL",
    email="mahimmittal20@gmail.com",
    phone="617-513-3554",
    location="Boston, 02121, MA, United States",
    linkedin=None,
    github=None,
    summary="Results-driven Business Analyst with over 8 years of experience in software implementation and product management, specializing in Salesforce Community Portal design and conversion of legacy systems. Proven ability to elicit requirements, develop user stories and functional specifications, and lead cross-functional teams to deliver impactful solutions. Adept in collaborating with stakeholders to drive business outcomes and enhance system performance.",
    skills=["Salesforce Community Portal", "Legacy System Conversion", "Business Process Mapping", "User Acceptance Testing (UAT)", "Requirements Elicitation", "Functional Specification Writing", "Stakeholder Management", "Communication", "Team Collaboration", "Problem Solving", "Project Management"],
    experience=[
        Experience(
            title="Senior Business Analyst",
            company="WebKorps",
            start_date="09/2023",
            end_date="Present",
            description="Facilitated requirements elicitation sessions with stakeholders, capturing crucial business objectives and aligning them with project goals. Developed comprehensive user stories and functional specifications for Salesforce Community Portal implementation, enhancing user engagement by 30%. Designed and implemented Salesforce Community Portals, ensuring seamless integration with existing property assessment systems. Oversaw the conversion of legacy systems to Salesforce, managing project phases from planning through execution, resulting in a 25% reduction in processing time. Created and executed user acceptance test (UAT) cases, ensuring solutions met all defined requirements and improved system reliability by 40%. Collaborated with cross-functional teams to deliver system enhancements, improving overall efficiency and user satisfaction ratings by 15%. Trained and mentored junior analysts, providing guidance on best practices in requirements gathering and documentation. Implemented business process maps that streamlined operations, achieving a 20% increase in workflow efficiency. Regularly communicated project updates and status reports to stakeholders, ensuring transparency and alignment throughout the project lifecycle. Utilized Agile methodologies to manage project timelines and deliverables, fostering a culture of continuous improvement."
        ),
        Experience(
            title="Business Analyst",
            company="IBM",
            start_date="01/2022",
            end_date="08/2023",
            description="Led cross-functional teams in the implementation of property tax systems, achieving project completion on time and within budget. Conducted in-depth analysis of legacy systems and developed strategies for their conversion to Salesforce, enhancing system functionality and user experience. Facilitated stakeholder workshops to gather and clarify business requirements, resulting in the creation of actionable project roadmaps. Drafted detailed functional specifications and user stories, ensuring clear communication of system requirements to development teams. Executed user acceptance testing (UAT) for new systems, identifying and resolving issues prior to launch, which improved user adoption rates by 35%. Developed and maintained business process maps that identified process inefficiencies, leading to a 15% reduction in operational costs. Collaborated with IT teams to integrate Salesforce with existing applications, improving data accuracy and accessibility. Provided project updates and key insights to executive management, facilitating informed decision-making. Mentored new team members on Salesforce functionalities and business analysis methodologies, enhancing team capacity. Participated in continuous improvement initiatives to enhance project delivery and operational performance."
        ),
        Experience(
            title="Junior Business Analyst",
            company="AmericanKorps",
            start_date="07/2017",
            end_date="12/2021",
            description="Assisted in gathering and documenting business requirements for software projects, ensuring alignment with client expectations. Supported the development of user stories and functional specifications for various technology projects. Participated in user acceptance testing (UAT), assisting in the identification and documentation of system defects. Collaborated with senior analysts to create business process maps, identifying areas for improvement. Engaged with stakeholders to gather feedback on system functionality, contributing to iterative design enhancements. Coordinated project timelines and deliverables, ensuring adherence to deadlines and project scope. Prepared project documentation and status reports for team meetings and stakeholder reviews. Conducted market research and analysis to inform project direction and strategy. Supported training sessions for end-users, enhancing overall system usability and user experience. Developed a repository of best practices and lessons learned for project documentation."
        ),
    ],
    education=[
        Education(
            degree="MS",
            major="Computer Science Engineering",
            university="Northeastern University",
            graduation_date="12/2024"
        )
    ],
    projects=[],
    certifications=["Salesforce Certified Administrator", "Certified Business Analysis Professional (CBAP)"]
)

class GenerateResumeRequest(BaseModel):
    job_description_text: str
    desired_filename_job_title: str 

@app.post("/generate_tailored_resume/", response_model=Dict)
async def generate_tailored_resume(request: GenerateResumeRequest):
    job_description_text = request.job_description_text

    # Create a dummy JobDescription for tailoring (OpenAI will use its description)
    dummy_job_description = JobDescription(
        title="placeholder", 
        company="placeholder",
        description=job_description_text,
        keywords=[]
    )
    
    # Tailor resume using OpenAI
    tailored_resume = tailor_resume(BASE_USER_RESUME, dummy_job_description)
    
    # Store the tailored resume with a unique ID
    resume_id = str(uuid.uuid4())
    generated_resumes_db[resume_id] = tailored_resume
    
    # Save to database for history
    db.save_resume(
        resume_id=resume_id,
        job_title=request.desired_filename_job_title,
        job_description=job_description_text,
        resume_data=tailored_resume.model_dump()
    )

    return {"resume_id": resume_id, "resume_data": tailored_resume.model_dump()}


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are invalid in filenames."""
    # Replace problematic characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    result = name
    for char in invalid_chars:
        result = result.replace(char, '-')
    return result

@app.get("/download_resume/pdf/{resume_id}/{desired_filename_job_title:path}")
async def download_resume_pdf(resume_id: str, desired_filename_job_title: str):
    if resume_id not in generated_resumes_db:
        raise HTTPException(status_code=404, detail="Generated resume not found")

    resume_to_download = generated_resumes_db[resume_id]
    
    # Sanitize the filename to remove invalid characters
    safe_job_title = sanitize_filename(desired_filename_job_title)
    filename = f"{resume_to_download.name.replace(' ', '_')}_{safe_job_title}_resume.pdf"

    pdf_path = generate_pdf_resume(resume_to_download)
    return FileResponse(path=pdf_path, media_type="application/pdf", filename=filename)

@app.get("/download_resume/word/{resume_id}/{desired_filename_job_title:path}")
async def download_resume_word(resume_id: str, desired_filename_job_title: str):
    if resume_id not in generated_resumes_db:
        raise HTTPException(status_code=404, detail="Generated resume not found")

    resume_to_download = generated_resumes_db[resume_id]

    # Sanitize the filename to remove invalid characters
    safe_job_title = sanitize_filename(desired_filename_job_title)
    filename = f"{resume_to_download.name.replace(' ', '_')}_{safe_job_title}_resume.docx"

    word_path = generate_word_resume(resume_to_download)
    return FileResponse(path=word_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)


# =============================================================================
# HISTORY ENDPOINTS
# =============================================================================

@app.get("/history/")
async def get_resume_history():
    """Get all previously generated resumes."""
    return db.get_all_resumes()

@app.get("/history/{resume_id}")
async def get_resume_from_history(resume_id: str):
    """Get a specific resume from history."""
    resume = db.get_resume(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found in history")
    
    # Also load into memory for downloads
    resume_data = resume["resume_data"]
    generated_resumes_db[resume_id] = Resume(**resume_data)
    
    return resume

@app.delete("/history/{resume_id}")
async def delete_resume_from_history(resume_id: str):
    """Delete a resume from history."""
    success = db.delete_resume(resume_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Also remove from memory
    if resume_id in generated_resumes_db:
        del generated_resumes_db[resume_id]
    
    return {"message": "Resume deleted successfully"}


# =============================================================================
# CHAT ENDPOINTS
# =============================================================================

class ChatRequest(BaseModel):
    resume_id: str
    message: str

@app.post("/chat/")
async def chat_about_resume(request: ChatRequest):
    """Ask questions about a generated resume."""
    # Get resume from memory or database
    if request.resume_id in generated_resumes_db:
        resume = generated_resumes_db[request.resume_id]
        resume_data = resume.model_dump()
    else:
        stored = db.get_resume(request.resume_id)
        if not stored:
            raise HTTPException(status_code=404, detail="Resume not found")
        resume_data = stored["resume_data"]
    
    # Get chat history
    chat_history = db.get_chat_history(request.resume_id)
    
    # Build messages for OpenAI
    messages = [
        {
            "role": "system", 
            "content": f"""You are a helpful assistant that answers questions about the following resume. 
            Be specific and reference actual content from the resume when answering.
            
            RESUME DATA:
            {resume_data}
            """
        }
    ]
    
    # Add chat history
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current message
    messages.append({"role": "user", "content": request.message})
    
    # Get response from OpenAI
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        assistant_response = response.choices[0].message.content
        
        # Save chat messages to database
        db.save_chat_message(request.resume_id, "user", request.message)
        db.save_chat_message(request.resume_id, "assistant", assistant_response)
        
        return {
            "response": assistant_response,
            "chat_history": db.get_chat_history(request.resume_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/chat/{resume_id}")
async def get_chat_history(resume_id: str):
    """Get chat history for a resume."""
    return db.get_chat_history(resume_id)

@app.delete("/chat/{resume_id}")
async def clear_chat_history(resume_id: str):
    """Clear chat history for a resume (keeps resume)."""
    conn = __import__('sqlite3').connect(db.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE resume_id = ?', (resume_id,))
    conn.commit()
    conn.close()
    return {"message": "Chat history cleared"}

