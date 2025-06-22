import gradio as gr
from production_career_toolkit import (
    generate_ai_resume_interface, generate_ai_cover_letter_interface,
    analyze_resume_interface, calculate_ats_interface, match_jobs_interface,
    calculate_perfection_interface, generate_linkedin_interface,
    analyze_skill_gaps_interface, create_dashboard_interface, chatbot_interface
)

def create_production_interface():
    """Create production-ready AI Career Toolkit interface."""
    
    # Professional CSS styling
    custom_css = """
    .gradio-container {
        max-width: 1600px !important;
        margin: auto !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .feature-tab {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .generate-btn {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
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
    .chat-btn {
        background: linear-gradient(45deg, #4facfe, #00f2fe) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    .metric-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #28a745; }
    .status-loading { background-color: #ffc107; }
    .status-offline { background-color: #dc3545; }
    """
    
    with gr.Blocks(css=custom_css, title="AI Career Toolkit Pro") as interface:
        
        # Main Header
        with gr.Row():
            gr.HTML("""
                <div class="main-header">
                    <h1>🚀 AI Career Toolkit Pro</h1>
                    <p>Production-Ready Career Development Platform with Real-Time AI Integration</p>
                    <div style="margin-top: 10px;">
                        <span class="status-indicator status-online"></span> Real-Time AI Models Active
                        <span style="margin-left: 20px;"><span class="status-indicator status-online"></span> Hugging Face API Connected</span>
                        <span style="margin-left: 20px;"><span class="status-indicator status-online"></span> Advanced Analytics Ready</span>
                    </div>
                </div>
            """)
        
        # Tab-based Professional Interface
        with gr.Tabs():
            
            # AI Content Generation Tab
            with gr.TabItem("🤖 AI Resume & Cover Letter"):
                gr.Markdown("### Real-Time AI Content Generation with Mistral-7B-Instruct")
                
                with gr.Row():
                    # AI Resume Generator
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📄 AI Resume Generator")
                        
                        with gr.Group():
                            resume_name = gr.Textbox(
                                label="Full Name",
                                placeholder="Enter your full name",
                                lines=1
                            )
                            
                            resume_role = gr.Textbox(
                                label="Target Position",
                                placeholder="e.g., Senior Software Engineer, Data Scientist",
                                lines=1
                            )
                            
                            resume_skills = gr.Textbox(
                                label="Core Skills",
                                placeholder="Python, Machine Learning, AWS, Project Management",
                                lines=3
                            )
                            
                            resume_experience = gr.Textbox(
                                label="Professional Experience",
                                placeholder="Describe your work experience with specific achievements and metrics",
                                lines=4
                            )
                            
                            resume_education = gr.Textbox(
                                label="Education & Certifications",
                                placeholder="Degrees, certifications, relevant coursework",
                                lines=2
                            )
                            
                            generate_resume_btn = gr.Button(
                                "🚀 Generate AI Resume",
                                variant="primary",
                                elem_classes=["generate-btn"]
                            )
                    
                    # AI Cover Letter Generator
                    with gr.Column(scale=1):
                        gr.Markdown("#### 💼 AI Cover Letter Generator")
                        
                        with gr.Group():
                            cl_name = gr.Textbox(
                                label="Full Name",
                                placeholder="Enter your full name",
                                lines=1
                            )
                            
                            cl_role = gr.Textbox(
                                label="Position Applying For",
                                placeholder="e.g., Software Engineer, Marketing Manager",
                                lines=1
                            )
                            
                            cl_company = gr.Textbox(
                                label="Company Name",
                                placeholder="Target company name",
                                lines=1
                            )
                            
                            cl_skills = gr.Textbox(
                                label="Relevant Skills",
                                placeholder="Key skills relevant to this position",
                                lines=3
                            )
                            
                            generate_cl_btn = gr.Button(
                                "✍️ Generate AI Cover Letter",
                                variant="secondary",
                                elem_classes=["analyze-btn"]
                            )
                
                # Output Section
                with gr.Row():
                    with gr.Column():
                        resume_output = gr.Textbox(
                            label="AI-Generated Resume",
                            lines=15,
                            interactive=False,
                            placeholder="Your AI-generated resume will appear here..."
                        )
                        resume_pdf = gr.File(
                            label="📥 Download Resume PDF",
                            interactive=False
                        )
                    
                    with gr.Column():
                        cl_output = gr.Textbox(
                            label="AI-Generated Cover Letter",
                            lines=15,
                            interactive=False,
                            placeholder="Your AI-generated cover letter will appear here..."
                        )
                        cl_pdf = gr.File(
                            label="📥 Download Cover Letter PDF",
                            interactive=False
                        )
            
            # Advanced Analysis Tab
            with gr.TabItem("📊 Resume Analysis & ATS"):
                gr.Markdown("### Advanced Resume Analysis with AI Insights")
                
                with gr.Row():
                    # Resume Upload & Analysis
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🔍 Resume Analyzer")
                        
                        with gr.Group():
                            analysis_upload = gr.File(
                                label="Upload Resume (PDF)",
                                file_types=[".pdf"],
                                type="filepath"
                            )
                            
                            with gr.Row():
                                analyze_btn = gr.Button(
                                    "🔍 Analyze Resume",
                                    variant="primary",
                                    elem_classes=["analyze-btn"]
                                )
                                
                                perfection_btn = gr.Button(
                                    "⭐ Perfection Score",
                                    variant="secondary",
                                    elem_classes=["analyze-btn"]
                                )
                    
                    # ATS Score Calculator
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🎯 ATS Match Calculator")
                        
                        with gr.Group():
                            ats_upload = gr.File(
                                label="Upload Resume (PDF)",
                                file_types=[".pdf"],
                                type="filepath"
                            )
                            
                            job_desc = gr.Textbox(
                                label="Job Description",
                                placeholder="Paste the complete job description here...",
                                lines=6
                            )
                            
                            ats_btn = gr.Button(
                                "🎯 Calculate ATS Score",
                                variant="primary",
                                elem_classes=["generate-btn"]
                            )
                
                # Analysis Results
                with gr.Row():
                    analysis_output = gr.Textbox(
                        label="Resume Analysis Results",
                        lines=20,
                        interactive=False,
                        placeholder="Upload a resume to see detailed analysis..."
                    )
                    
                    ats_output = gr.Textbox(
                        label="ATS Compatibility Report",
                        lines=20,
                        interactive=False,
                        placeholder="Upload resume and job description for ATS analysis..."
                    )
            
            # Job Matching & Skills Tab
            with gr.TabItem("🎯 Job Matching & Skills"):
                gr.Markdown("### AI-Powered Job Matching and Skill Development")
                
                with gr.Row():
                    # Job Matcher
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🔗 Advanced Job Matcher")
                        
                        with gr.Group():
                            user_skills = gr.Textbox(
                                label="Your Skills",
                                placeholder="Python, React, Project Management, Data Analysis...",
                                lines=4
                            )
                            
                            match_jobs_btn = gr.Button(
                                "🔍 Find Matching Jobs",
                                variant="primary",
                                elem_classes=["generate-btn"]
                            )
                            
                            job_matches = gr.Textbox(
                                label="Job Matching Results",
                                lines=15,
                                interactive=False,
                                placeholder="Enter your skills to discover matching opportunities..."
                            )
                    
                    # Skill Gap Analyzer
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📈 Skill Gap Analysis")
                        
                        with gr.Group():
                            current_skills = gr.Textbox(
                                label="Current Skills",
                                placeholder="List your current technical and soft skills",
                                lines=3
                            )
                            
                            target_job = gr.Textbox(
                                label="Target Job Role",
                                placeholder="e.g., Software Engineer, Data Scientist, Product Manager",
                                lines=1
                            )
                            
                            gap_analysis_btn = gr.Button(
                                "📊 Analyze Skill Gaps",
                                variant="secondary",
                                elem_classes=["analyze-btn"]
                            )
                            
                            gap_results = gr.Textbox(
                                label="Skill Gap Analysis & Learning Roadmap",
                                lines=15,
                                interactive=False,
                                placeholder="Enter skills and target role for personalized learning path..."
                            )
            
            # LinkedIn & Career Insights Tab
            with gr.TabItem("💼 LinkedIn & Career Dashboard"):
                gr.Markdown("### Professional Branding and Career Intelligence")
                
                with gr.Row():
                    # LinkedIn Generator
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🌐 LinkedIn Summary Generator")
                        
                        with gr.Group():
                            linkedin_name = gr.Textbox(
                                label="Full Name",
                                placeholder="Your professional name",
                                lines=1
                            )
                            
                            linkedin_role = gr.Textbox(
                                label="Professional Title",
                                placeholder="Your current or target role",
                                lines=1
                            )
                            
                            linkedin_skills = gr.Textbox(
                                label="Core Competencies",
                                placeholder="Your key professional skills",
                                lines=3
                            )
                            
                            linkedin_exp = gr.Textbox(
                                label="Key Achievements",
                                placeholder="Notable accomplishments and experience highlights",
                                lines=4
                            )
                            
                            linkedin_btn = gr.Button(
                                "✨ Generate LinkedIn Summary",
                                variant="primary",
                                elem_classes=["generate-btn"]
                            )
                            
                            linkedin_output = gr.Textbox(
                                label="AI-Generated LinkedIn Summary",
                                lines=12,
                                interactive=False,
                                placeholder="Your professional LinkedIn summary will appear here..."
                            )
                    
                    # Career Dashboard
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📈 Career Insights Dashboard")
                        
                        with gr.Group():
                            dashboard_resume = gr.File(
                                label="Resume (Optional)",
                                file_types=[".pdf"],
                                type="filepath"
                            )
                            
                            dashboard_skills = gr.Textbox(
                                label="Your Complete Skillset",
                                placeholder="All your professional skills",
                                lines=3
                            )
                            
                            dashboard_target = gr.Textbox(
                                label="Career Target",
                                placeholder="Your target position or career goal",
                                lines=1
                            )
                            
                            dashboard_btn = gr.Button(
                                "🚀 Generate Career Dashboard",
                                variant="primary",
                                elem_classes=["dashboard-btn"]
                            )
                            
                            dashboard_summary = gr.Textbox(
                                label="Executive Career Summary",
                                lines=12,
                                interactive=False,
                                placeholder="Upload resume and enter details for comprehensive career insights..."
                            )
                            
                            dashboard_viz = gr.File(
                                label="📊 Career Insights Visualization",
                                interactive=False
                            )
            
            # AI Career Chatbot Tab
            with gr.TabItem("💬 AI Career Advisor"):
                gr.Markdown("### Real-Time Career Consultation with AI Expert")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("#### 🤖 AI Career Advisor Chat")
                        
                        chatbot = gr.Chatbot(
                            label="Career Advisor Conversation",
                            height=600,
                            placeholder="Start a conversation with your AI career advisor..."
                        )
                        
                        with gr.Row():
                            msg = gr.Textbox(
                                label="Your Question",
                                placeholder="Ask about resumes, interviews, career planning, salary negotiation...",
                                lines=2,
                                scale=4
                            )
                            
                            send_btn = gr.Button(
                                "Send",
                                variant="primary",
                                elem_classes=["chat-btn"],
                                scale=1
                            )
                        
                        clear_btn = gr.Button(
                            "Clear Conversation",
                            variant="secondary"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### 💡 Quick Career Tips")
                        gr.HTML("""
                            <div class="metric-card">
                                <h4>🎯 Popular Questions</h4>
                                <ul>
                                    <li>"How can I improve my resume?"</li>
                                    <li>"What skills should I learn for data science?"</li>
                                    <li>"How do I negotiate salary?"</li>
                                    <li>"What are good interview questions to ask?"</li>
                                    <li>"How do I transition to tech?"</li>
                                </ul>
                            </div>
                            
                            <div class="metric-card">
                                <h4>🚀 Career Resources</h4>
                                <ul>
                                    <li>Industry salary benchmarks</li>
                                    <li>Skill development roadmaps</li>
                                    <li>Interview preparation guides</li>
                                    <li>Networking strategies</li>
                                    <li>Career transition planning</li>
                                </ul>
                            </div>
                        """)
        
        # Professional Footer with Usage Guidelines
        with gr.Row():
            gr.Markdown("""
                ### 🎯 Production Features Overview
                
                **Real-Time AI Generation**: Powered by Mistral-7B-Instruct for high-quality content creation
                
                **Advanced Analytics**: TF-IDF similarity, keyword matching, and comprehensive scoring algorithms
                
                **Professional PDF Export**: Formatted documents ready for immediate use
                
                **Career Intelligence**: Market insights, salary data, and growth projections
                
                **Expert AI Advisor**: Real-time career consultation and personalized guidance
                
                ---
                
                ### 💼 Best Practices for Maximum Results
                
                **Content Quality**: Provide detailed, specific information for better AI-generated results
                
                **ATS Optimization**: Use job-specific keywords and maintain professional formatting
                
                **Skill Development**: Focus on in-demand skills with high market growth rates
                
                **Professional Branding**: Maintain consistency across all career documents
                
                **Continuous Improvement**: Regularly update profiles based on market trends
            """)
        
        # Connect all interface functions
        
        # Resume and Cover Letter Generation
        generate_resume_btn.click(
            fn=generate_ai_resume_interface,
            inputs=[resume_name, resume_role, resume_skills, resume_experience, resume_education],
            outputs=[resume_output, resume_pdf]
        )
        
        generate_cl_btn.click(
            fn=generate_ai_cover_letter_interface,
            inputs=[cl_name, cl_role, cl_company, cl_skills],
            outputs=[cl_output, cl_pdf]
        )
        
        # Resume Analysis
        analyze_btn.click(
            fn=analyze_resume_interface,
            inputs=[analysis_upload],
            outputs=[analysis_output]
        )
        
        perfection_btn.click(
            fn=calculate_perfection_interface,
            inputs=[analysis_upload],
            outputs=[analysis_output]
        )
        
        # ATS Calculator
        ats_btn.click(
            fn=calculate_ats_interface,
            inputs=[ats_upload, job_desc],
            outputs=[ats_output]
        )
        
        # Job Matching and Skills
        match_jobs_btn.click(
            fn=match_jobs_interface,
            inputs=[user_skills],
            outputs=[job_matches]
        )
        
        gap_analysis_btn.click(
            fn=analyze_skill_gaps_interface,
            inputs=[current_skills, target_job],
            outputs=[gap_results]
        )
        
        # LinkedIn and Dashboard
        linkedin_btn.click(
            fn=generate_linkedin_interface,
            inputs=[linkedin_name, linkedin_role, linkedin_skills, linkedin_exp],
            outputs=[linkedin_output]
        )
        
        dashboard_btn.click(
            fn=create_dashboard_interface,
            inputs=[dashboard_resume, dashboard_skills, dashboard_target],
            outputs=[dashboard_summary, dashboard_viz]
        )
        
        # Chatbot functionality
        def respond(message, history):
            bot_message = chatbot_interface(message, history)
            history.append((message, bot_message))
            return history, ""
        
        send_btn.click(
            fn=respond,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            fn=respond,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        clear_btn.click(
            lambda: [],
            outputs=[chatbot]
        )
        
        # Add professional examples
        gr.Examples(
            examples=[
                [
                    "Alexandra Chen",
                    "Senior Machine Learning Engineer",
                    "Python, TensorFlow, PyTorch, Kubernetes, AWS, MLOps, Deep Learning, Computer Vision, NLP, Statistical Analysis",
                    "Senior ML Engineer at TechCorp (2022-2024): Led development of computer vision models achieving 95% accuracy, deployed 20+ ML models to production serving 1M+ users daily, reduced inference time by 40% through optimization. ML Engineer at DataFlow (2020-2022): Built recommendation systems increasing user engagement by 35%, implemented A/B testing framework, mentored 3 junior engineers.",
                    "Master of Science in Computer Science, Stanford University (2018-2020). Bachelor of Engineering in Computer Science, UC Berkeley (2014-2018). AWS Machine Learning Specialty Certification, Google Cloud Professional ML Engineer."
                ],
                [
                    "Marcus Rodriguez",
                    "Product Manager",
                    "Product Strategy, User Research, Data Analysis, Agile, SQL, Tableau, A/B Testing, Roadmapping, Stakeholder Management, Market Research",
                    "Senior Product Manager at GrowthCo (2021-2024): Launched 5 major features resulting in 60% user growth, managed $2M product budget, led cross-functional team of 15 engineers and designers. Product Analyst at StartupXYZ (2019-2021): Analyzed user behavior data to drive product decisions, increased conversion rates by 25% through feature optimization, conducted 50+ user interviews.",
                    "MBA from Wharton School (2017-2019). Bachelor of Science in Business Administration, UCLA (2013-2017). Google Analytics Certified, Certified Scrum Product Owner."
                ]
            ],
            inputs=[resume_name, resume_role, resume_skills, resume_experience, resume_education]
        )
    
    return interface

# Launch the production application
if __name__ == "__main__":
    try:
        app = create_production_interface()
        
        app.launch(
            server_name="0.0.0.0",
            server_port=5000,
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"Error: Failed to start the production application - {e}")