import openai
import json

from .models import Resume, JobDescription

def tailor_resume(original_resume: Resume, job_description: JobDescription) -> Resume:

    # Convert resume and job description to text for OpenAI
    original_resume_text = original_resume.model_dump_json(indent=2)
    job_description_text = job_description.description # Use only the description text

    prompt = f"""
    Tailor the provided resume (Original Resume) to the given Job Description. 
    
    **ALWAYS KEEP THE FOLLOWING FIELDS EXACTLY AS THEY ARE IN THE ORIGINAL RESUME:**
    - name
    - email
    - phone
    - linkedin (if present)
    - github (if present)
    - For each experience entry: company, start_date, end_date
    - For each education entry: degree, major, university, graduation_date
    - location (from the resume)

    **MODIFY THE FOLLOWING FIELDS TO ALIGN WITH THE JOB DESCRIPTION:**
    - summary (CRITICAL: The summary should mention"8+ years of experience")
    - skills (see SKILLS FORMATTING below)
    - For each experience entry: title, description (rephrase to highlight relevant achievements and keywords from JD)
    - projects (if present, rephrase to highlight relevant aspects)
    - certifications (update or rephrase to match job description needs, if applicable)

    **CRITICAL FORMATTING REQUIREMENT FOR SKILLS:**
    - Skills MUST be grouped by category
    - Each skill entry in the skills array should be in format: "Category Name: skill1, skill2, skill3, ..."
    - Create 3-5 relevant categories based on the job description
    - Each category MUST around minimum 6-7 relevant skills (more for technical categories, fewer for soft skills)
    - Prioritize skills mentioned in the job description
    - Example format: ["Technical Skills: Python, SQL, Tableau, Power BI, Excel, JIRA, Git, AWS", "Soft Skills: Communication, Leadership, Problem Solving, Teamwork"]

    **CRITICAL FORMATTING REQUIREMENT FOR EXPERIENCE DESCRIPTIONS:**
    - Use the PIPE character "|" to separate each bullet point
    - Do NOT use newlines or bullet symbols in the description
    - STRICT MINIMUM: Each bullet MUST contain AT LEAST 20 words. Bullets under 20 words are REJECTED.
    - Each bullet MUST include: specific action verb + detailed context + quantified result with numbers
    - Number of bullets per role:
      * Senior roles: 10-12 bullets (each 22-30 words)
      * Mid-level roles: 8-10 bullets (each 15-22 words)
      * Junior roles: 6-8 bullets (each 12-15 words)
    
    MANDATORY EXAMPLE FORMAT - Each bullet must be this detailed:
    "Spearheaded the design and implementation of an automated data validation framework using Python and SQL, reducing data errors by 47% and saving 120 hours of manual review time monthly across the finance department|Collaborated with cross-functional team of 12 stakeholders including product managers, developers, and QA engineers to deliver a $1.8M Salesforce Community Portal integration project, achieving 98% user adoption within first quarter|Architected and deployed comprehensive business intelligence dashboards in Tableau serving 200+ daily active users, enabling real-time tracking of 35 critical KPIs and improving executive decision-making speed by 60%"

    Original Resume:\n{original_resume_text}

    Job Description:\n{job_description_text}

    Return the tailored resume in the exact same JSON format as the original resume, ensuring it strictly adheres to the schema. 
    Only return the JSON object.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o", # Or a more advanced model like gpt-4
            messages=[
                {"role": "system", "content": "You are a professional resume writer who creates DETAILED, VERBOSE bullet points. Every experience bullet point you write MUST be at least 20-30 words long with specific metrics and quantified achievements. Never write short, generic bullets. Always include specific numbers, percentages, dollar amounts, team sizes, and timeframes. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        tailored_resume_data = json.loads(response.choices[0].message.content)

        # Ensure fixed fields are truly fixed after OpenAI processing
        final_resume = Resume(**tailored_resume_data)
        final_resume.name = original_resume.name
        final_resume.email = original_resume.email
        final_resume.phone = original_resume.phone
        final_resume.linkedin = original_resume.linkedin
        final_resume.github = original_resume.github
        final_resume.location = original_resume.location

        # Ensure company, start_date, end_date for experience, and all education fields are fixed
        if len(original_resume.experience) == len(final_resume.experience):
            for i in range(len(original_resume.experience)):
                final_resume.experience[i].company = original_resume.experience[i].company
                final_resume.experience[i].start_date = original_resume.experience[i].start_date
                final_resume.experience[i].end_date = original_resume.experience[i].end_date
        
        if len(original_resume.education) == len(final_resume.education):
            for i in range(len(original_resume.education)):
                final_resume.education[i].degree = original_resume.education[i].degree
                final_resume.education[i].major = original_resume.education[i].major
                final_resume.education[i].university = original_resume.education[i].university
                final_resume.education[i].graduation_date = original_resume.education[i].graduation_date

        return final_resume

    except Exception as e:
        print(f"Error tailoring resume with OpenAI: {e}")
        return original_resume
