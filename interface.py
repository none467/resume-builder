import gradio as gr
from career_toolkit import (
    generate_resume, generate_cover_letter, analyze_uploaded_resume,
    calculate_ats_match, match_user_jobs, calculate_resume_perfection,
    generate_linkedin_profile, analyze_skill_gaps, create_dashboard
)

def create_comprehensive_interface():
    """Create comprehensive AI Career Toolkit interface."""
    
    # Custom CSS for professional styling
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
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
    .analyze-btn {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    .dashboard-btn {
        background: linear-gradient(45deg, #f093fb, #f5576c) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    """
    
    with gr.Blocks(css=custom_css, title="AI Career Toolkit") as interface:
        
        # Header
        gr.Markdown(
            """
            # AI Career Toolkit - Complete Career Development Platform
            
            Transform your career with AI-powered tools for resume building, job matching, skill analysis, and career insights.
            
            ---
            """
        )
        
        # Tab-based interface for different tools
        with gr.Tabs():
            
            # Tab 1: Resume & Cover Letter Generation
            with gr.TabItem("Resume & Cover Letter Generator"):
                gr.Markdown("### Generate Professional Resume and Cover Letter")
                
                with gr.Row():
                    # Resume Section
                    with gr.Column(scale=1):
                        gr.Markdown("#### Resume Generator")
                        
                        name_input = gr.Textbox(
                            label="Full Name",
                            placeholder="Enter your full name",
                            lines=1
                        )
                        
                        job_role_input = gr.Textbox(
                            label="Target Job Role",
                            placeholder="e.g., Software Engineer, Marketing Manager, Data Scientist",
                            lines=1
                        )
                        
                        skills_input = gr.Textbox(
                            label="Skills",
                            placeholder="List your key skills (e.g., Python, Project Management, Digital Marketing)",
                            lines=3
                        )
                        
                        experience_input = gr.Textbox(
                            label="Work Experience",
                            placeholder="Describe your work experience, including company names, positions, and key achievements",
                            lines=4
                        )
                        
                        education_input = gr.Textbox(
                            label="Education",
                            placeholder="Your educational background (degrees, institutions, certifications)",
                            lines=3
                        )
                        
                        generate_resume_btn = gr.Button(
                            "Generate Professional Resume",
                            variant="primary",
                            elem_classes=["generate-btn"]
                        )
                    
                    # Cover Letter Section
                    with gr.Column(scale=1):
                        gr.Markdown("#### Cover Letter Generator")
                        
                        cl_name_input = gr.Textbox(
                            label="Full Name",
                            placeholder="Enter your full name",
                            lines=1
                        )
                        
                        cl_job_role_input = gr.Textbox(
                            label="Target Job Role",
                            placeholder="e.g., Software Engineer, Marketing Manager",
                            lines=1
                        )
                        
                        company_input = gr.Textbox(
                            label="Company Name",
                            placeholder="Enter the company you're applying to",
                            lines=1
                        )
                        
                        cl_skills_input = gr.Textbox(
                            label="Key Skills",
                            placeholder="List your most relevant skills for this position",
                            lines=3
                        )
                        
                        generate_cover_letter_btn = gr.Button(
                            "Generate Cover Letter",
                            variant="secondary",
                            elem_classes=["analyze-btn"]
                        )
                
                # Output sections
                with gr.Row():
                    with gr.Column():
                        resume_output = gr.Textbox(
                            label="Generated Resume",
                            lines=12,
                            interactive=False
                        )
                        resume_pdf = gr.File(label="Download Resume PDF")
                    
                    with gr.Column():
                        cover_letter_output = gr.Textbox(
                            label="Generated Cover Letter",
                            lines=12,
                            interactive=False
                        )
                        cover_letter_pdf = gr.File(label="Download Cover Letter PDF")
            
            # Tab 2: Resume Analysis & ATS
            with gr.TabItem("Resume Analysis & ATS Checker"):
                gr.Markdown("### Analyze Your Resume and Check ATS Compatibility")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### Resume Analyzer")
                        
                        resume_upload = gr.File(
                            label="Upload Resume (PDF)",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        
                        analyze_resume_btn = gr.Button(
                            "Analyze Resume",
                            variant="primary",
                            elem_classes=["analyze-btn"]
                        )
                        
                        perfection_score_btn = gr.Button(
                            "Calculate Perfection Score",
                            variant="secondary",
                            elem_classes=["analyze-btn"]
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### ATS Match Calculator")
                        
                        ats_resume_upload = gr.File(
                            label="Upload Resume (PDF)",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        
                        job_description_input = gr.Textbox(
                            label="Job Description",
                            placeholder="Paste the job description here...",
                            lines=8
                        )
                        
                        calculate_ats_btn = gr.Button(
                            "Calculate ATS Score",
                            variant="primary",
                            elem_classes=["generate-btn"]
                        )
                
                # Analysis outputs
                with gr.Row():
                    with gr.Column():
                        analysis_output = gr.Textbox(
                            label="Resume Analysis Report",
                            lines=15,
                            interactive=False
                        )
                    
                    with gr.Column():
                        ats_output = gr.Textbox(
                            label="ATS Match Report",
                            lines=15,
                            interactive=False
                        )
            
            # Tab 3: Job Matching & Skill Gap Analysis
            with gr.TabItem("Job Matching & Skill Development"):
                gr.Markdown("### Find Matching Jobs and Identify Skill Gaps")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### Job Matcher")
                        
                        user_skills_input = gr.Textbox(
                            label="Your Skills",
                            placeholder="Enter your skills separated by commas",
                            lines=3
                        )
                        
                        match_jobs_btn = gr.Button(
                            "Find Matching Jobs",
                            variant="primary",
                            elem_classes=["generate-btn"]
                        )
                        
                        job_match_output = gr.Textbox(
                            label="Job Matching Results",
                            lines=12,
                            interactive=False
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### Skill Gap Analyzer")
                        
                        current_skills_input = gr.Textbox(
                            label="Current Skills",
                            placeholder="Enter your current skills",
                            lines=3
                        )
                        
                        target_job_input = gr.Textbox(
                            label="Target Job Role",
                            placeholder="Enter your target job role",
                            lines=1
                        )
                        
                        analyze_gaps_btn = gr.Button(
                            "Analyze Skill Gaps",
                            variant="secondary",
                            elem_classes=["analyze-btn"]
                        )
                        
                        skill_gap_output = gr.Textbox(
                            label="Skill Gap Analysis",
                            lines=12,
                            interactive=False
                        )
            
            # Tab 4: LinkedIn Profile & Career Insights
            with gr.TabItem("LinkedIn Profile & Career Dashboard"):
                gr.Markdown("### Generate LinkedIn Summary and Career Insights")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### LinkedIn Summary Generator")
                        
                        linkedin_name = gr.Textbox(
                            label="Full Name",
                            placeholder="Your full name",
                            lines=1
                        )
                        
                        linkedin_role = gr.Textbox(
                            label="Professional Role",
                            placeholder="Your current or target role",
                            lines=1
                        )
                        
                        linkedin_skills = gr.Textbox(
                            label="Key Skills",
                            placeholder="Your top skills",
                            lines=3
                        )
                        
                        linkedin_experience = gr.Textbox(
                            label="Experience Highlights",
                            placeholder="Key achievements and experience",
                            lines=4
                        )
                        
                        generate_linkedin_btn = gr.Button(
                            "Generate LinkedIn Summary",
                            variant="primary",
                            elem_classes=["generate-btn"]
                        )
                        
                        linkedin_output = gr.Textbox(
                            label="LinkedIn Summary",
                            lines=12,
                            interactive=False
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### Career Insights Dashboard")
                        
                        dashboard_resume = gr.File(
                            label="Upload Resume (PDF) - Optional",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        
                        dashboard_skills = gr.Textbox(
                            label="Your Skills",
                            placeholder="Enter all your skills",
                            lines=3
                        )
                        
                        dashboard_target_job = gr.Textbox(
                            label="Target Job Role",
                            placeholder="Your target position",
                            lines=1
                        )
                        
                        create_dashboard_btn = gr.Button(
                            "Create Career Dashboard",
                            variant="primary",
                            elem_classes=["dashboard-btn"]
                        )
                        
                        dashboard_output = gr.Textbox(
                            label="Career Insights Summary",
                            lines=12,
                            interactive=False
                        )
                        
                        dashboard_chart = gr.Image(
                            label="Career Insights Visualization",
                            type="filepath"
                        )
        
        # Instructions and Tips
        with gr.Row():
            gr.Markdown(
                """
                ### How to Use This Career Toolkit:
                
                **Resume & Cover Letter**: Generate professional documents tailored to specific roles and companies.
                
                **Resume Analysis**: Upload your current resume to get detailed feedback and improvement suggestions.
                
                **ATS Checker**: Compare your resume against job descriptions to optimize for Applicant Tracking Systems.
                
                **Job Matching**: Discover roles that match your skillset and see your compatibility scores.
                
                **Skill Gap Analysis**: Identify skills you need to develop for your target role with learning resources.
                
                **LinkedIn Profile**: Create compelling LinkedIn summaries that attract recruiters and connections.
                
                **Career Dashboard**: Get comprehensive insights into your career readiness and development path.
                
                ### Tips for Best Results:
                - Be specific and detailed in your inputs
                - Use industry-relevant keywords
                - Upload high-quality, text-readable PDF resumes
                - Update your skills regularly as you learn new ones
                """
            )
        
        # Connect all the button functions
        
        # Resume and Cover Letter Generation
        generate_resume_btn.click(
            fn=generate_resume,
            inputs=[name_input, job_role_input, skills_input, experience_input, education_input],
            outputs=[resume_output, resume_pdf]
        )
        
        generate_cover_letter_btn.click(
            fn=generate_cover_letter,
            inputs=[cl_name_input, cl_job_role_input, company_input, cl_skills_input],
            outputs=[cover_letter_output, cover_letter_pdf]
        )
        
        # Resume Analysis
        analyze_resume_btn.click(
            fn=analyze_uploaded_resume,
            inputs=[resume_upload],
            outputs=[analysis_output]
        )
        
        perfection_score_btn.click(
            fn=calculate_resume_perfection,
            inputs=[resume_upload],
            outputs=[analysis_output]
        )
        
        # ATS Calculator
        calculate_ats_btn.click(
            fn=calculate_ats_match,
            inputs=[ats_resume_upload, job_description_input],
            outputs=[ats_output]
        )
        
        # Job Matching
        match_jobs_btn.click(
            fn=match_user_jobs,
            inputs=[user_skills_input],
            outputs=[job_match_output]
        )
        
        # Skill Gap Analysis
        analyze_gaps_btn.click(
            fn=analyze_skill_gaps,
            inputs=[current_skills_input, target_job_input],
            outputs=[skill_gap_output]
        )
        
        # LinkedIn Profile Generation
        generate_linkedin_btn.click(
            fn=generate_linkedin_profile,
            inputs=[linkedin_name, linkedin_role, linkedin_skills, linkedin_experience],
            outputs=[linkedin_output]
        )
        
        # Career Dashboard
        create_dashboard_btn.click(
            fn=create_dashboard,
            inputs=[dashboard_resume, dashboard_skills, dashboard_target_job],
            outputs=[dashboard_output, dashboard_chart]
        )
        
        # Add examples for the main resume generation
        gr.Examples(
            examples=[
                [
                    "John Smith",
                    "Software Engineer",
                    "Python, JavaScript, React, Node.js, SQL, Git, Docker, AWS, API Development, Testing",
                    "Software Developer at TechCorp (2021-2023): Developed web applications using React and Node.js, improved system performance by 30%. Junior Developer at StartupXYZ (2020-2021): Built RESTful APIs and worked on database optimization.",
                    "Bachelor of Science in Computer Science, University of Technology (2016-2020). Relevant coursework: Data Structures, Algorithms, Web Development, Database Management."
                ],
                [
                    "Sarah Johnson",
                    "Data Scientist",
                    "Python, R, Machine Learning, SQL, Statistics, Pandas, NumPy, Scikit-learn, TensorFlow, Data Visualization",
                    "Data Analyst at DataTech (2022-2023): Built predictive models that improved customer retention by 25%. Research Assistant at University Lab (2021-2022): Analyzed large datasets and published findings in peer-reviewed journals.",
                    "Master of Science in Data Science, State University (2020-2022). Bachelor of Science in Statistics, Local College (2016-2020). Relevant certifications: Google Analytics, Tableau Desktop Specialist."
                ]
            ],
            inputs=[name_input, job_role_input, skills_input, experience_input, education_input]
        )
    
    return interface

# Launch the application
if __name__ == "__main__":
    try:
        app = create_comprehensive_interface()
        
        app.launch(
            server_name="0.0.0.0",
            server_port=5000,
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"Error: Failed to start the application - {e}")