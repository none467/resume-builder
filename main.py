import gradio as gr
from fpdf import FPDF
import os
import tempfile
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import AI libraries, but make them optional for faster startup
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    AI_AVAILABLE = True
    logger.info("AI libraries loaded successfully")
except ImportError as e:
    logger.warning(f"AI libraries not available: {e}. Using fallback mode.")
    AI_AVAILABLE = False

class ResumeBuilder:
    def __init__(self):
        """Initialize the Resume Builder with optional AI model and tokenizer."""
        self.model_name = "microsoft/phi-1_5"
        self.tokenizer = None
        self.model = None
        self.ai_enabled = AI_AVAILABLE
        if self.ai_enabled:
            self.load_model()
    
    def load_model(self):
        """Load the Hugging Face model and tokenizer."""
        if not AI_AVAILABLE:
            logger.warning("AI libraries not available, using structured fallback")
            return
            
        try:
            logger.info("Loading AI model and tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                device_map="auto"
            )
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.ai_enabled = False
            logger.info("Switching to fallback mode")
    
    def generate_resume_content(self, name, job_role, skills, experience, education):
        """Generate resume content using the AI model or structured approach."""
        # If AI is not available or disabled, use structured approach
        if not self.ai_enabled or self.model is None or self.tokenizer is None:
            return self.create_intelligent_resume(name, job_role, skills, experience, education)
            
        try:
            # Create a structured prompt for the AI model
            prompt = f"""Generate a professional resume content for the following person:

Name: {name}
Job Role: {job_role}
Skills: {skills}
Experience: {experience}
Education: {education}

Please create a well-structured professional resume with the following sections:
1. Professional Summary
2. Skills
3. Work Experience
4. Education
5. Additional qualifications if applicable

Make it professional, concise, and tailored for the {job_role} position."""

            # Tokenize the input
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=500,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (remove the prompt)
            resume_content = generated_text[len(prompt):].strip()
            
            # If the generated content is too short or empty, use intelligent structured approach
            if len(resume_content) < 100:
                resume_content = self.create_intelligent_resume(name, job_role, skills, experience, education)
            
            return resume_content
            
        except Exception as e:
            logger.error(f"Error generating resume content: {e}")
            # Use intelligent structured approach if AI generation fails
            return self.create_intelligent_resume(name, job_role, skills, experience, education)
    
    def create_intelligent_resume(self, name, job_role, skills, experience, education):
        """Create an intelligent structured resume with dynamic content."""
        # Process skills into a formatted list
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        formatted_skills = '\n'.join([f"• {skill}" for skill in skills_list])
        
        # Create professional summary based on role and skills
        summary = self.generate_summary(job_role, skills_list)
        
        # Format experience section
        formatted_experience = self.format_experience(experience)
        
        # Format education section
        formatted_education = self.format_education(education)
        
        # Generate role-specific achievements
        achievements = self.generate_achievements(job_role)
        
        resume_content = f"""
PROFESSIONAL RESUME

{name.upper()}
{job_role}

PROFESSIONAL SUMMARY
{summary}

CORE SKILLS
{formatted_skills}

PROFESSIONAL EXPERIENCE
{formatted_experience}

EDUCATION
{formatted_education}

KEY ACHIEVEMENTS & QUALIFICATIONS
{achievements}
"""
        return resume_content.strip()
    
    def generate_summary(self, job_role, skills_list):
        """Generate a professional summary based on role and skills."""
        role_keywords = {
            'software': ['development', 'programming', 'technical solutions', 'software engineering'],
            'engineer': ['engineering', 'technical expertise', 'problem-solving', 'innovation'],
            'manager': ['leadership', 'team management', 'strategic planning', 'organizational growth'],
            'marketing': ['brand development', 'campaign management', 'market analysis', 'customer engagement'],
            'data': ['data analysis', 'insights', 'statistical modeling', 'data-driven decisions'],
            'design': ['creative solutions', 'user experience', 'visual design', 'innovative concepts'],
            'sales': ['client relationships', 'revenue generation', 'market penetration', 'sales strategy']
        }
        
        # Find relevant keywords for the role
        relevant_keywords = []
        for key, keywords in role_keywords.items():
            if key.lower() in job_role.lower():
                relevant_keywords.extend(keywords)
        
        # Use top skills
        top_skills = skills_list[:3] if len(skills_list) >= 3 else skills_list
        skills_text = ', '.join(top_skills)
        
        if relevant_keywords:
            focus_area = relevant_keywords[0]
            return f"Results-driven {job_role} with proven expertise in {skills_text}. Specialized in {focus_area} with a track record of delivering high-quality solutions and driving organizational success through innovative approaches and collaborative leadership."
        else:
            return f"Dedicated {job_role} professional with comprehensive experience in {skills_text}. Committed to excellence and continuous improvement, with strong analytical skills and the ability to adapt to dynamic environments while delivering measurable results."
    
    def format_experience(self, experience):
        """Format the experience section with better structure."""
        if not experience.strip():
            return "Please add your work experience details."
        
        # Split by common separators and format
        experiences = re.split(r'[.]\s*(?=[A-Z])|[\n]+', experience)
        formatted_exp = []
        
        for exp in experiences:
            exp = exp.strip()
            if len(exp) > 10:  # Only include substantial entries
                if not exp.endswith('.'):
                    exp += '.'
                formatted_exp.append(f"• {exp}")
        
        return '\n'.join(formatted_exp) if formatted_exp else experience
    
    def format_education(self, education):
        """Format the education section with better structure."""
        if not education.strip():
            return "Please add your educational background."
        
        # Split by common separators and format
        edu_items = re.split(r'[.]\s*(?=[A-Z])|[\n]+', education)
        formatted_edu = []
        
        for item in edu_items:
            item = item.strip()
            if len(item) > 5:  # Only include substantial entries
                if not item.endswith('.'):
                    item += '.'
                formatted_edu.append(f"• {item}")
        
        return '\n'.join(formatted_edu) if formatted_edu else education
    
    def generate_achievements(self, job_role):
        """Generate role-specific achievements and qualifications."""
        role_achievements = {
            'software': [
                "Proficient in modern development methodologies and best practices",
                "Experience with version control systems and collaborative development",
                "Strong debugging and optimization skills",
                "Continuous learning mindset for emerging technologies"
            ],
            'engineer': [
                "Strong analytical and problem-solving capabilities",
                "Experience with technical documentation and specifications",
                "Proven ability to work with cross-functional teams",
                "Commitment to quality and engineering excellence"
            ],
            'manager': [
                "Proven leadership and team development experience",
                "Strong communication and interpersonal skills",
                "Experience in project management and deadline delivery",
                "Strategic thinking and decision-making abilities"
            ],
            'marketing': [
                "Data-driven approach to campaign optimization",
                "Strong understanding of digital marketing channels",
                "Creative content development and brand messaging",
                "Market research and competitive analysis skills"
            ],
            'data': [
                "Proficiency in statistical analysis and data visualization",
                "Experience with data cleaning and preprocessing",
                "Strong presentation skills for technical findings",
                "Understanding of business intelligence principles"
            ],
            'design': [
                "Strong aesthetic sense and attention to detail",
                "User-centered design approach and methodology",
                "Proficiency in industry-standard design tools",
                "Collaborative approach to creative problem-solving"
            ],
            'sales': [
                "Strong negotiation and closing skills",
                "Customer relationship management expertise",
                "Understanding of sales processes and CRM systems",
                "Goal-oriented mindset with proven track record"
            ]
        }
        
        # Find relevant achievements
        achievements = []
        for key, achievs in role_achievements.items():
            if key.lower() in job_role.lower():
                achievements.extend(achievs)
                break
        
        # Default achievements if no specific role found
        if not achievements:
            achievements = [
                "Strong problem-solving and analytical abilities",
                "Excellent communication and collaboration skills",
                "Adaptable to new technologies and methodologies",
                "Detail-oriented with strong organizational capabilities"
            ]
        
        return '\n'.join([f"• {achievement}" for achievement in achievements])
    
    def generate_cover_letter_content(self, name, job_role, company, skills):
        """Generate cover letter content using intelligent structured approach."""
        # Process skills into a list
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        top_skills = skills_list[:4] if len(skills_list) >= 4 else skills_list
        
        # Generate role-specific opening and content
        opening = self.generate_cover_letter_opening(job_role, company)
        body = self.generate_cover_letter_body(job_role, top_skills, company)
        closing = self.generate_cover_letter_closing(company)
        
        cover_letter_content = f"""
COVER LETTER

{name}
{job_role} Application

Date: [Current Date]

Dear Hiring Manager,

{opening}

{body}

{closing}

Sincerely,
{name}
"""
        return cover_letter_content.strip()
    
    def generate_cover_letter_opening(self, job_role, company):
        """Generate an engaging opening paragraph for the cover letter."""
        return f"I am writing to express my strong interest in the {job_role} position at {company}. Having researched your organization, I am impressed by your commitment to excellence and innovation, and I am excited about the opportunity to contribute to your team's continued success."
    
    def generate_cover_letter_body(self, job_role, skills, company):
        """Generate the body paragraphs of the cover letter."""
        skills_text = ', '.join(skills)
        
        # Role-specific content
        role_content = {
            'software': f"My technical expertise in {skills_text} aligns perfectly with the requirements for this role. I have successfully developed and deployed applications that have improved user experience and system performance. My passion for clean, efficient code and collaborative development makes me an ideal fit for {company}'s technical team.",
            'engineer': f"With my strong foundation in {skills_text}, I bring both technical proficiency and problem-solving capabilities to this role. My experience in project execution and technical documentation, combined with my commitment to engineering excellence, positions me well to contribute to {company}'s innovative projects.",
            'manager': f"My leadership experience and skills in {skills_text} have enabled me to successfully guide teams and deliver results. I excel at strategic planning, team development, and cross-functional collaboration. I am confident that my management approach and vision align with {company}'s leadership values.",
            'marketing': f"My expertise in {skills_text} has driven successful campaigns and brand growth throughout my career. I understand the importance of data-driven decision making and creative strategy execution. I am excited about the opportunity to bring my marketing insights and innovative approach to {company}.",
            'data': f"My analytical skills and proficiency in {skills_text} have enabled me to extract meaningful insights from complex datasets. I excel at translating data into actionable business strategies and presenting findings to stakeholders. I am eager to apply my data expertise to help {company} make informed decisions.",
            'design': f"My design philosophy centers on user-centered solutions, supported by my skills in {skills_text}. I have successfully created intuitive interfaces and compelling visual experiences that enhance user engagement. I am excited to contribute my creative vision and technical skills to {company}'s design initiatives.",
            'sales': f"My sales experience and skills in {skills_text} have consistently resulted in exceeding targets and building strong client relationships. I understand the importance of consultative selling and customer satisfaction. I am confident that my proven track record and relationship-building abilities will contribute to {company}'s continued growth."
        }
        
        # Find matching content or use default
        body_content = None
        for key, content in role_content.items():
            if key.lower() in job_role.lower():
                body_content = content
                break
        
        if not body_content:
            body_content = f"My professional experience and skills in {skills_text} have prepared me well for this role. I am committed to excellence, continuous learning, and contributing meaningfully to organizational success. I believe my background and enthusiasm make me a strong candidate for this position at {company}."
        
        return body_content
    
    def generate_cover_letter_closing(self, company):
        """Generate a professional closing paragraph."""
        return f"I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to {company}'s success. Thank you for considering my application. I look forward to hearing from you soon."
    
    def create_pdf(self, resume_content, name):
        """Create a PDF from the resume content using fpdf."""
        try:
            # Create PDF instance
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Set margins
            pdf.set_left_margin(20)
            pdf.set_right_margin(20)
            pdf.set_top_margin(20)
            
            # Split content into lines and add to PDF
            lines = resume_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(5)  # Add small space for empty lines
                    continue
                
                # Check if line is a header (all caps or contains certain keywords)
                if (line.isupper() and len(line) > 3) or any(keyword in line.upper() for keyword in ['SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'QUALIFICATIONS']):
                    pdf.set_font("Arial", 'B', 14)  # Bold for headers
                    pdf.ln(5)
                    pdf.cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    pdf.ln(2)
                    pdf.set_font("Arial", size=12)  # Reset to normal font
                else:
                    # Handle long lines by wrapping them
                    if len(line) > 80:
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 80:
                                current_line += word + " "
                            else:
                                pdf.cell(0, 8, current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                                current_line = word + " "
                        if current_line:
                            pdf.cell(0, 8, current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    else:
                        pdf.cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
            
            # Save PDF to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix=f"{name.replace(' ', '_')}_resume_")
            pdf.output(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            raise Exception(f"Failed to create PDF: {e}")
    
    def create_cover_letter_pdf(self, cover_letter_content, name, company):
        """Create a PDF from the cover letter content using fpdf."""
        try:
            # Create PDF instance
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Set margins
            pdf.set_left_margin(20)
            pdf.set_right_margin(20)
            pdf.set_top_margin(20)
            
            # Split content into lines and add to PDF
            lines = cover_letter_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(3)  # Add small space for empty lines
                    continue
                
                # Check if line is a header
                if line == "COVER LETTER":
                    pdf.set_font("Arial", 'B', 16)  # Larger bold for main header
                    pdf.ln(5)
                    pdf.cell(0, 12, line.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
                    pdf.ln(5)
                    pdf.set_font("Arial", size=12)  # Reset to normal font
                elif "Application" in line or line.startswith("Date:") or line.startswith("Dear") or line.startswith("Sincerely"):
                    pdf.set_font("Arial", 'B', 12)  # Bold for important elements
                    pdf.cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    if line.startswith("Dear"):
                        pdf.ln(3)
                    pdf.set_font("Arial", size=12)  # Reset to normal font
                else:
                    # Handle long lines by wrapping them
                    if len(line) > 85:
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 85:
                                current_line += word + " "
                            else:
                                pdf.cell(0, 6, current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                                current_line = word + " "
                        if current_line:
                            pdf.cell(0, 6, current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    else:
                        pdf.cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    
                    # Add extra space after paragraphs
                    if len(line) > 50:
                        pdf.ln(2)
            
            # Save PDF to temporary file
            company_clean = company.replace(' ', '_').replace('/', '_')
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", 
                                                   prefix=f"{name.replace(' ', '_')}_cover_letter_{company_clean}_")
            pdf.output(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating cover letter PDF: {e}")
            raise Exception(f"Failed to create cover letter PDF: {e}")

# Initialize the resume builder (without loading heavy AI models initially)
resume_builder = ResumeBuilder()

def generate_resume(name, job_role, skills, experience, education):
    """Main function to generate resume and create PDF."""
    try:
        # Validate inputs
        if not all([name.strip(), job_role.strip(), skills.strip(), experience.strip(), education.strip()]):
            return "Error: Please fill in all fields to generate your resume.", None
        
        # Generate resume content
        resume_content = resume_builder.generate_resume_content(name, job_role, skills, experience, education)
        
        # Create PDF
        pdf_path = resume_builder.create_pdf(resume_content, name)
        
        return f"Resume generated successfully for {name}!\n\n{resume_content[:500]}...", pdf_path
        
    except Exception as e:
        logger.error(f"Error in generate_resume: {e}")
        return f"Error generating resume: {str(e)}", None

def generate_cover_letter(name, job_role, company, skills):
    """Main function to generate cover letter and create PDF."""
    try:
        # Validate inputs
        if not all([name.strip(), job_role.strip(), company.strip(), skills.strip()]):
            return "Error: Please fill in all fields to generate your cover letter.", None
        
        # Generate cover letter content
        cover_letter_content = resume_builder.generate_cover_letter_content(name, job_role, company, skills)
        
        # Create PDF with cover letter naming
        pdf_path = resume_builder.create_cover_letter_pdf(cover_letter_content, name, company)
        
        return f"Cover letter generated successfully for {name} applying to {company}!\n\n{cover_letter_content[:400]}...", pdf_path
        
    except Exception as e:
        logger.error(f"Error in generate_cover_letter: {e}")
        return f"Error generating cover letter: {str(e)}", None

# Create Gradio interface
def create_interface():
    """Create and configure the Gradio interface."""
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1100px !important;
        margin: auto !important;
    }
    .input-container {
        margin-bottom: 15px !important;
    }
    .generate-btn {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    .cover-letter-btn {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    """
    
    with gr.Blocks(css=custom_css, title="AI Resume & Cover Letter Builder", theme=gr.themes.Soft()) as interface:
        
        # Header
        gr.Markdown(
            """
            # AI-Powered Resume & Cover Letter Builder
            
            Create professional resumes and cover letters instantly! Fill in your details below and generate polished, 
            professional documents tailored to your career goals.
            
            ---
            """
        )
        
        # Input Sections
        with gr.Row():
            # Resume Section
            with gr.Column(scale=1):
                gr.Markdown("### Resume Generator")
                
                name_input = gr.Textbox(
                    label="Full Name",
                    placeholder="Enter your full name",
                    lines=1,
                    elem_classes=["input-container"]
                )
                
                job_role_input = gr.Textbox(
                    label="Target Job Role",
                    placeholder="e.g., Software Engineer, Marketing Manager, Data Scientist",
                    lines=1,
                    elem_classes=["input-container"]
                )
                
                skills_input = gr.Textbox(
                    label="Skills",
                    placeholder="List your key skills (e.g., Python, Project Management, Digital Marketing)",
                    lines=3,
                    elem_classes=["input-container"]
                )
                
                experience_input = gr.Textbox(
                    label="Work Experience",
                    placeholder="Describe your work experience, including company names, positions, and key achievements",
                    lines=4,
                    elem_classes=["input-container"]
                )
                
                education_input = gr.Textbox(
                    label="Education",
                    placeholder="Your educational background (degrees, institutions, certifications)",
                    lines=3,
                    elem_classes=["input-container"]
                )
            
            # Cover Letter Section
            with gr.Column(scale=1):
                gr.Markdown("### Cover Letter Generator")
                
                cl_name_input = gr.Textbox(
                    label="Full Name",
                    placeholder="Enter your full name",
                    lines=1,
                    elem_classes=["input-container"]
                )
                
                cl_job_role_input = gr.Textbox(
                    label="Target Job Role",
                    placeholder="e.g., Software Engineer, Marketing Manager, Data Scientist",
                    lines=1,
                    elem_classes=["input-container"]
                )
                
                company_input = gr.Textbox(
                    label="Company Name",
                    placeholder="Enter the company you're applying to",
                    lines=1,
                    elem_classes=["input-container"]
                )
                
                cl_skills_input = gr.Textbox(
                    label="Key Skills",
                    placeholder="List your most relevant skills for this position",
                    lines=3,
                    elem_classes=["input-container"]
                )
        
        # Generate Buttons
        with gr.Row():
            with gr.Column():
                generate_resume_btn = gr.Button(
                    "Generate Professional Resume",
                    variant="primary",
                    size="lg",
                    elem_classes=["generate-btn"]
                )
            with gr.Column():
                generate_cover_letter_btn = gr.Button(
                    "Generate Cover Letter",
                    variant="secondary",
                    size="lg",
                    elem_classes=["cover-letter-btn"]
                )
        
        # Output Sections
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Generated Resume")
                
                resume_output_text = gr.Textbox(
                    label="Resume Preview",
                    lines=12,
                    max_lines=15,
                    interactive=False,
                    placeholder="Your generated resume will appear here..."
                )
                
                resume_pdf_output = gr.File(
                    label="Download Resume (PDF)",
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("### Generated Cover Letter")
                
                cover_letter_output_text = gr.Textbox(
                    label="Cover Letter Preview",
                    lines=12,
                    max_lines=15,
                    interactive=False,
                    placeholder="Your generated cover letter will appear here..."
                )
                
                cover_letter_pdf_output = gr.File(
                    label="Download Cover Letter (PDF)",
                    interactive=False
                )
        
        # Instructions
        with gr.Row():
            gr.Markdown(
                """
                ### Tips for Best Results:
                - **Be Specific**: Include specific skills, technologies, and achievements
                - **Use Keywords**: Include industry-relevant keywords for your target role
                - **Quantify Achievements**: Use numbers and metrics where possible
                - **Research the Company**: For cover letters, mention specific company details when possible
                
                ### How it Works:
                1. Fill in your information in the respective sections
                2. Click "Generate Professional Resume" or "Generate Cover Letter"
                3. Review and download your professional PDF documents
                """
            )
        
        # Connect the generate buttons to the functions
        generate_resume_btn.click(
            fn=generate_resume,
            inputs=[name_input, job_role_input, skills_input, experience_input, education_input],
            outputs=[resume_output_text, resume_pdf_output]
        )
        
        generate_cover_letter_btn.click(
            fn=generate_cover_letter,
            inputs=[cl_name_input, cl_job_role_input, company_input, cl_skills_input],
            outputs=[cover_letter_output_text, cover_letter_pdf_output]
        )
        
        # Add examples
        gr.Examples(
            examples=[
                [
                    "John Smith",
                    "Software Engineer",
                    "Python, JavaScript, React, Node.js, SQL, Git, Docker, AWS",
                    "Software Developer at TechCorp (2021-2023): Developed web applications using React and Node.js, improved system performance by 30%. Junior Developer at StartupXYZ (2020-2021): Built RESTful APIs and worked on database optimization.",
                    "Bachelor of Science in Computer Science, University of Technology (2016-2020). Relevant coursework: Data Structures, Algorithms, Web Development, Database Management."
                ],
                [
                    "Sarah Johnson",
                    "Digital Marketing Manager",
                    "SEO, SEM, Social Media Marketing, Google Analytics, Content Strategy, Email Marketing, PPC Campaigns",
                    "Digital Marketing Specialist at MarketingPro (2022-2023): Managed social media campaigns with 150% engagement increase. Marketing Coordinator at BrandCorp (2020-2022): Developed content strategies and managed email campaigns with 25% open rate improvement.",
                    "Bachelor of Arts in Marketing, State University (2016-2020). Google Analytics Certified, HubSpot Content Marketing Certification."
                ]
            ],
            inputs=[name_input, job_role_input, skills_input, experience_input, education_input]
        )
    
    return interface

# Launch the application
if __name__ == "__main__":
    try:
        # Create and launch the interface
        app = create_interface()
        
        # Launch with specific settings
        app.launch(
            server_name="0.0.0.0",
            server_port=5000,
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        logger.error(f"Failed to launch application: {e}")
        print(f"Error: Failed to start the application - {e}")
