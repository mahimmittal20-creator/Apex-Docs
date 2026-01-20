import openai
import json

from .models import Resume, JobDescription

def tailor_resume(original_resume: Resume, job_description: JobDescription) -> Resume:

    # Convert resume and job description to text for OpenAI
    original_resume_text = original_resume.model_dump_json(indent=2)
    job_description_text = job_description.description # Use only the description text

    prompt = f"""
    GENERATE a resume for the Job Description below. Use the Template Resume ONLY for structure (companies, dates, education, personal info).

    **KEEP THESE FIXED FROM TEMPLATE (do not change):**
    - name, email, phone, location, linkedin, github
    - Company names: WebKorps, IBM, AmericanKorps
    - Employment dates: start_date, end_date for each role
    - Education: degree, major, university, graduation_date

    **GENERATE THESE BASED ON JOB DESCRIPTION (create new content):**
    
    1. **SUMMARY** - Write a professional summary (MINIMUM 75 words):
       - MUST start with "8+ years of experience"
       - Matches the target role from the job description
       - Highlights relevant expertise, key skills, and achievements for THIS specific job
       - Include industry keywords from the job description
    
    2. **JOB TITLES** - Generate titles matching the target role:
       - WebKorps (most recent): Senior level title (e.g., "Senior [ Relevant Role from JD]" or relavant JD title)
       - IBM (middle): Mid level title (e.g., "[Relevant Role from JD]" or relavant JD title)
       - AmericanKorps (earliest): Junior level title (e.g., "Junior [Relevant Role from JD]" or "Associate [Role]")
       - NEVER use "Business Analyst" unless applying for BA roles
    
    3. **SKILLS** - Generate skills from the job description:
       - Group into 3-5 categories: "Category Name: skill1, skill2, skill3, ..."
       - Each category: 6-7 relevant skills
       - Prioritize skills mentioned in the job description
       - Example: ["Technical Skills: Python, SQL, AWS, Docker", "Soft Skills: Leadership, Communication"]
    
    4. **EXPERIENCE DESCRIPTIONS** - CRITICAL: WRITE LONG, DETAILED BULLETS
       - Use PIPE "|" to separate bullet points (no newlines)
       - MANDATORY MINIMUM WORD COUNTS (COUNT YOUR WORDS!):
         * WebKorps (Senior): 10 bullets, MINIMUM 28 words each - NEVER less than 25 words
         * IBM (Mid): 8 bullets, MINIMUM 22 words each - NEVER less than 20 words
         * AmericanKorps (Junior): 6 bullets, MINIMUM 16 words each - NEVER less than 15 words
       
       ❌ BAD (TOO SHORT - 11 words): "Architected simulated avionics systems in C++, increasing simulator performance by 40%"
       
       ✅ GOOD Senior (30 words): "Architected and deployed high-performance simulated avionics systems using advanced C++ design patterns and multithreading techniques, resulting in a 40% improvement in simulator performance while reducing memory consumption by 25% across all test environments"
       
       ✅ GOOD Mid (22 words): "Led cross-functional development team of 8 engineers to successfully deliver customer-facing flight simulation portal ahead of schedule, increasing user engagement metrics by 40% within first quarter"
       
       ✅ GOOD Junior (17 words): "Developed and maintained comprehensive automated test scripts using Selenium and Python frameworks, improving overall code coverage from 60% to 85%"
       
       EACH BULLET MUST INCLUDE: action verb + specific context + technology/tools + quantified result + business impact
    
    5. **CERTIFICATIONS** - Generate 1 or 2 relevant certifications:
       - Must match the target role/industry
       - Include any certifications mentioned in job description as required/preferred
       - DO NOT include certificates unless relevant to the job

    Template Resume (for structure only):\n{original_resume_text}

    Job Description:\n{job_description_text}

    Return valid JSON matching the template resume schema.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume writer. CRITICAL: Write LONG, DETAILED bullets. Summary: 75+ words. MINIMUM bullet lengths - Senior: 28+ words, Mid: 22+ words, Junior: 16+ words. SHORT BULLETS ARE REJECTED. Each bullet needs: action verb + context + tools/tech + metric + business impact. Example Senior bullet (30 words): 'Architected and deployed high-performance data systems using Kafka and Spark with advanced caching strategies, processing 2M daily transactions while reducing latency by 65% and cutting infrastructure costs by $50K annually'. Output valid JSON."},
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
