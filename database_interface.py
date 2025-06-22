import gradio as gr
from production_career_toolkit import (
    generate_ai_resume_interface, generate_ai_cover_letter_interface,
    analyze_resume_interface, calculate_ats_interface, match_jobs_interface,
    calculate_perfection_interface, generate_linkedin_interface,
    analyze_skill_gaps_interface, create_dashboard_interface, chatbot_interface
)
from database_manager import get_db_manager
import json
from datetime import datetime
import hashlib

# Global user session management
current_user_id = None

def get_or_create_user_session(name=None):
    """Get or create user session."""
    global current_user_id
    if current_user_id is None:
        db = get_db_manager()
        user_data = db.create_or_get_user(name=name)
        if user_data:
            current_user_id = user_data['user_id']
    return current_user_id

def enhanced_resume_generation(name, role, skills, experience, education):
    """Enhanced resume generation with database storage."""
    user_id = get_or_create_user_session(name)
    db = get_db_manager()
    
    # Log analytics
    db.log_analytics(user_id, "resume_generation_started", {
        "job_role": role,
        "skills_count": len(skills.split(',')) if skills else 0
    })
    
    # Generate resume
    result_text, pdf_path = generate_ai_resume_interface(name, role, skills, experience, education)
    
    if pdf_path and "successfully" in result_text:
        # Save to database
        resume_data = {
            'name': f"{name} - {role} Resume",
            'content': result_text,
            'job_role': role,
            'skills': skills.split(',') if skills else [],
            'experience': experience,
            'education': education,
            'pdf_path': pdf_path
        }
        
        resume_id = db.save_resume(user_id, resume_data)
        
        if resume_id:
            db.log_analytics(user_id, "resume_generated", {
                "resume_id": resume_id,
                "job_role": role
            })
            result_text += f"\n\n📁 Resume saved to your account (ID: {resume_id})"
    
    return result_text, pdf_path

def enhanced_cover_letter_generation(name, role, company, skills):
    """Enhanced cover letter generation with database storage."""
    user_id = get_or_create_user_session(name)
    db = get_db_manager()
    
    # Log analytics
    db.log_analytics(user_id, "cover_letter_generation_started", {
        "company": company,
        "job_role": role
    })
    
    # Generate cover letter
    result_text, pdf_path = generate_ai_cover_letter_interface(name, role, company, skills)
    
    if pdf_path and "successfully" in result_text:
        # Save to database
        cover_letter_data = {
            'company_name': company,
            'job_role': role,
            'content': result_text,
            'pdf_path': pdf_path
        }
        
        cover_letter_id = db.save_cover_letter(user_id, cover_letter_data)
        
        if cover_letter_id:
            db.log_analytics(user_id, "cover_letter_generated", {
                "cover_letter_id": cover_letter_id,
                "company": company
            })
            result_text += f"\n\n📁 Cover letter saved to your account (ID: {cover_letter_id})"
    
    return result_text, pdf_path

def enhanced_resume_analysis(resume_file):
    """Enhanced resume analysis with database storage."""
    user_id = get_or_create_user_session()
    db = get_db_manager()
    
    if user_id:
        db.log_analytics(user_id, "resume_analysis_started", {
            "file_name": resume_file.name if resume_file else None
        })
    
    result = analyze_resume_interface(resume_file)
    
    if user_id and result and "Error" not in str(result):
        db.log_analytics(user_id, "resume_analysis_completed")
    
    return result

def enhanced_ats_calculation(resume_file, job_description):
    """Enhanced ATS calculation with database storage."""
    user_id = get_or_create_user_session()
    db = get_db_manager()
    
    if user_id:
        db.log_analytics(user_id, "ats_calculation_started", {
            "job_description_length": len(job_description) if job_description else 0
        })
    
    result = calculate_ats_interface(resume_file, job_description)
    
    if user_id and result and "Error" not in str(result):
        db.log_analytics(user_id, "ats_calculation_completed")
    
    return result

def enhanced_skill_gap_analysis(current_skills, target_job):
    """Enhanced skill gap analysis with database storage."""
    user_id = get_or_create_user_session()
    db = get_db_manager()
    
    if user_id:
        db.log_analytics(user_id, "skill_gap_analysis_started", {
            "target_job": target_job,
            "current_skills_count": len(current_skills.split(',')) if current_skills else 0
        })
        
        # Save skill assessment
        assessment_data = {
            'target_role': target_job,
            'current_skills': current_skills.split(',') if current_skills else [],
            'missing_skills': [],  # Would be populated from analysis result
            'skill_gap_score': 0   # Would be calculated from analysis
        }
        
        assessment_id = db.save_skill_assessment(user_id, assessment_data)
    
    result = analyze_skill_gaps_interface(current_skills, target_job)
    
    if user_id and result and "Error" not in str(result):
        db.log_analytics(user_id, "skill_gap_analysis_completed", {
            "assessment_id": assessment_id if 'assessment_id' in locals() else None
        })
    
    return result

def enhanced_chatbot_interface(message, history):
    """Enhanced chatbot with conversation storage."""
    user_id = get_or_create_user_session()
    db = get_db_manager()
    
    # Generate response
    bot_response = chatbot_interface(message, history)
    
    # Save to database
    if user_id:
        session_id = hashlib.md5(f"{user_id}_{datetime.now().date()}".encode()).hexdigest()[:16]
        
        db.save_chat_message(
            user_id=user_id,
            user_message=message,
            ai_response=bot_response,
            session_id=session_id,
            category="career_advice"
        )
        
        db.log_analytics(user_id, "chat_message_sent", {
            "message_length": len(message),
            "response_length": len(bot_response)
        })
    
    history.append((message, bot_response))
    return history, ""

def get_user_history():
    """Get user's document history."""
    user_id = get_or_create_user_session()
    if not user_id:
        return "Please generate a resume or cover letter first to view your history."
    
    db = get_db_manager()
    dashboard_data = db.get_user_dashboard_data(user_id)
    
    if not dashboard_data:
        return "No history found."
    
    # Format history report
    stats = dashboard_data.get('stats', {})
    resumes = dashboard_data.get('resumes', [])
    cover_letters = dashboard_data.get('cover_letters', [])
    
    history_report = f"""
USER DASHBOARD & HISTORY
========================

📊 ACCOUNT STATISTICS:
• Total Resumes: {stats.get('total_resumes', 0)}
• Total Cover Letters: {stats.get('total_cover_letters', 0)}
• Total Applications: {stats.get('total_applications', 0)}
• Average Resume Score: {stats.get('avg_resume_score', 0):.1f}/100

📄 RECENT RESUMES ({len(resumes)}):
"""
    
    for i, resume in enumerate(resumes[:5], 1):
        created_date = resume['created_at'].strftime("%Y-%m-%d") if resume['created_at'] else 'Unknown'
        history_report += f"{i}. {resume['resume_name']} - {resume['job_role']} ({created_date})\n"
    
    history_report += f"""
💼 RECENT COVER LETTERS ({len(cover_letters)}):
"""
    
    for i, cl in enumerate(cover_letters[:5], 1):
        created_date = cl['created_at'].strftime("%Y-%m-%d") if cl['created_at'] else 'Unknown'
        history_report += f"{i}. {cl['company_name']} - {cl['job_role']} ({created_date})\n"
    
    # Usage analytics
    analytics = dashboard_data.get('analytics', [])
    if analytics:
        history_report += f"""
📈 RECENT ACTIVITY:
"""
        action_counts = {}
        for action in analytics:
            action_type = action['action_type']
            action_counts[action_type] = action_counts.get(action_type, 0) + action['count']
        
        for action_type, count in action_counts.items():
            history_report += f"• {action_type.replace('_', ' ').title()}: {count} times\n"
    
    return history_report

def search_user_documents(search_term):
    """Search user's documents."""
    user_id = get_or_create_user_session()
    if not user_id or not search_term.strip():
        return "Please enter a search term and ensure you have documents to search."
    
    db = get_db_manager()
    resumes = db.search_resumes(user_id, search_term)
    
    if not resumes:
        return f"No documents found matching '{search_term}'"
    
    search_results = f"""
SEARCH RESULTS FOR: "{search_term}"
==================================

Found {len(resumes)} matching document(s):

"""
    
    for i, resume in enumerate(resumes, 1):
        created_date = resume['created_at'].strftime("%Y-%m-%d") if resume['created_at'] else 'Unknown'
        search_results += f"{i}. {resume['resume_name']}\n"
        search_results += f"   Role: {resume['job_role']}\n"
        search_results += f"   Created: {created_date}\n"
        search_results += f"   Score: {resume['analysis_score']}/100\n\n"
    
    # Log search analytics
    db.log_analytics(user_id, "document_search", {
        "search_term": search_term,
        "results_count": len(resumes)
    })
    
    return search_results

def create_database_enhanced_interface():
    """Create the database-enhanced interface."""
    
    # Premium CSS (same as before)
    premium_css = """
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        --secondary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --accent-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --dark-gradient: linear-gradient(135deg, #434343 0%, #000000 100%);
        --glass-bg: rgba(255, 255, 255, 0.25);
        --glass-border: rgba(255, 255, 255, 0.18);
        --neon-blue: #00e0ff;
        --cyber-purple: #a100ff;
        --silver-white: #f5f7fa;
        --text-primary: #2c3e50;
        --text-secondary: #7f8c8d;
        --shadow-light: 0 8px 32px rgba(31, 38, 135, 0.37);
        --shadow-heavy: 0 15px 35px rgba(31, 38, 135, 0.2);
        --border-radius: 16px;
        --transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .gradio-container {
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #00C6FF 100%) !important;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated Background */
    .gradio-container::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(-45deg, #00C6FF, #0072FF, #667eea, #764ba2);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        z-index: -1;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glass Morphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: var(--border-radius) !important;
        padding: 30px !important;
        margin: 20px !important;
        box-shadow: var(--shadow-light) !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 40px rgba(31, 38, 135, 0.3) !important;
        background: rgba(255, 255, 255, 0.2) !important;
    }
    
    .hero-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--border-radius);
        padding: 60px 40px;
        margin: 20px;
        text-align: center;
        box-shadow: var(--shadow-heavy);
        position: relative;
        overflow: hidden;
        animation: slideInUp 1s ease-out;
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif !important;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px !important;
        position: relative;
        z-index: 1;
        animation: fadeInScale 1.2s ease-out 0.3s both;
    }
    
    .hero-subtitle {
        font-size: 1.3rem !important;
        color: rgba(255, 255, 255, 0.9) !important;
        margin-bottom: 30px !important;
        position: relative;
        z-index: 1;
        animation: fadeInScale 1.2s ease-out 0.6s both;
    }
    
    .btn-premium {
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px 30px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
        box-shadow: 0 8px 15px rgba(0, 114, 255, 0.3) !important;
    }
    
    .btn-premium:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 25px rgba(0, 114, 255, 0.4) !important;
        background: linear-gradient(135deg, #0072FF 0%, #00C6FF 100%) !important;
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px 30px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
        box-shadow: 0 8px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .input-premium {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 16px !important;
        transition: var(--transition) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    .output-premium {
        background: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        max-height: 400px !important;
        overflow-y: auto !important;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    """
    
    with gr.Blocks(css=premium_css, title="AI Career Toolkit Pro - Database Enhanced") as interface:
        
        # Hero Section
        with gr.Row():
            gr.HTML("""
                <div class="hero-section">
                    <h1 class="hero-title">AI Career Toolkit Pro</h1>
                    <p class="hero-subtitle">Database-Enhanced Career Development Platform with User History & Analytics</p>
                    <div style="color: rgba(255, 255, 255, 0.8); margin-top: 20px;">
                        🗄️ PostgreSQL Database Connected • 📊 User Analytics Enabled • 📁 Document History Saved
                    </div>
                </div>
            """)
        
        # Main Application Tabs
        with gr.Tabs():
            
            # AI Content Generation Tab
            with gr.TabItem("🚀 AI Generation"):
                with gr.Row():
                    # Resume Generator
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 📄 AI Resume Generator")
                        gr.Markdown("*With automatic database storage*")
                        
                        resume_name = gr.Textbox(
                            label="Full Name",
                            placeholder="Enter your full name",
                            elem_classes=["input-premium"]
                        )
                        
                        resume_role = gr.Textbox(
                            label="Target Position",
                            placeholder="e.g., Senior Software Engineer",
                            elem_classes=["input-premium"]
                        )
                        
                        resume_skills = gr.Textbox(
                            label="Core Skills",
                            placeholder="Python, Machine Learning, AWS",
                            lines=3,
                            elem_classes=["input-premium"]
                        )
                        
                        resume_experience = gr.Textbox(
                            label="Professional Experience",
                            placeholder="Describe your work experience",
                            lines=4,
                            elem_classes=["input-premium"]
                        )
                        
                        resume_education = gr.Textbox(
                            label="Education & Certifications",
                            placeholder="Degrees, certifications",
                            lines=2,
                            elem_classes=["input-premium"]
                        )
                        
                        generate_resume_btn = gr.Button(
                            "🚀 Generate & Save Resume",
                            elem_classes=["btn-premium"]
                        )
                    
                    # Cover Letter Generator
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 💼 AI Cover Letter Generator")
                        gr.Markdown("*Stored with application tracking*")
                        
                        cl_name = gr.Textbox(
                            label="Full Name",
                            placeholder="Enter your full name",
                            elem_classes=["input-premium"]
                        )
                        
                        cl_role = gr.Textbox(
                            label="Position Applying For",
                            placeholder="Target position",
                            elem_classes=["input-premium"]
                        )
                        
                        cl_company = gr.Textbox(
                            label="Company Name",
                            placeholder="Target company",
                            elem_classes=["input-premium"]
                        )
                        
                        cl_skills = gr.Textbox(
                            label="Relevant Skills",
                            placeholder="Key skills for this role",
                            lines=3,
                            elem_classes=["input-premium"]
                        )
                        
                        generate_cl_btn = gr.Button(
                            "✍️ Generate & Save Cover Letter",
                            elem_classes=["btn-secondary"]
                        )
                
                # Output Section
                with gr.Row():
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 📋 Generated Resume")
                        resume_output = gr.Textbox(
                            label="AI-Generated Resume",
                            lines=15,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
                        resume_pdf = gr.File(label="📥 Download Resume PDF")
                    
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 📝 Generated Cover Letter")
                        cl_output = gr.Textbox(
                            label="AI-Generated Cover Letter",
                            lines=15,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
                        cl_pdf = gr.File(label="📥 Download Cover Letter PDF")
            
            # Analysis Tab
            with gr.TabItem("📊 Analysis & ATS"):
                with gr.Row():
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 🔍 Resume Analyzer")
                        
                        analysis_upload = gr.File(
                            label="Upload Resume (PDF)",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        
                        analyze_btn = gr.Button(
                            "🔍 Analyze & Track",
                            elem_classes=["btn-secondary"]
                        )
                        
                        analysis_output = gr.Textbox(
                            label="Analysis Results",
                            lines=20,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
                    
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 🎯 ATS Calculator")
                        
                        ats_upload = gr.File(
                            label="Upload Resume (PDF)",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        
                        job_desc = gr.Textbox(
                            label="Job Description",
                            placeholder="Paste job description",
                            lines=6,
                            elem_classes=["input-premium"]
                        )
                        
                        ats_btn = gr.Button(
                            "🎯 Calculate ATS Score",
                            elem_classes=["btn-premium"]
                        )
                        
                        ats_output = gr.Textbox(
                            label="ATS Results",
                            lines=20,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
            
            # Skills & Jobs Tab
            with gr.TabItem("🎯 Skills & Jobs"):
                with gr.Row():
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 🔗 Job Matcher")
                        
                        user_skills = gr.Textbox(
                            label="Your Skills",
                            placeholder="List your skills",
                            lines=4,
                            elem_classes=["input-premium"]
                        )
                        
                        match_jobs_btn = gr.Button(
                            "🔍 Find Jobs",
                            elem_classes=["btn-premium"]
                        )
                        
                        job_matches = gr.Textbox(
                            label="Job Results",
                            lines=15,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
                    
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 📈 Skill Gap Analysis")
                        
                        current_skills = gr.Textbox(
                            label="Current Skills",
                            placeholder="Your current skills",
                            lines=3,
                            elem_classes=["input-premium"]
                        )
                        
                        target_job = gr.Textbox(
                            label="Target Job Role",
                            placeholder="Target position",
                            elem_classes=["input-premium"]
                        )
                        
                        gap_analysis_btn = gr.Button(
                            "📊 Analyze & Save",
                            elem_classes=["btn-secondary"]
                        )
                        
                        gap_results = gr.Textbox(
                            label="Gap Analysis",
                            lines=15,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
            
            # User Dashboard Tab
            with gr.TabItem("📊 My Dashboard"):
                with gr.Row():
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 📁 Document History")
                        
                        history_btn = gr.Button(
                            "📊 View My History",
                            elem_classes=["btn-premium"]
                        )
                        
                        history_output = gr.Textbox(
                            label="Your Account History",
                            lines=20,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
                    
                    with gr.Column(elem_classes=["glass-card"]):
                        gr.Markdown("### 🔍 Search Documents")
                        
                        search_input = gr.Textbox(
                            label="Search Term",
                            placeholder="Search your resumes and documents",
                            elem_classes=["input-premium"]
                        )
                        
                        search_btn = gr.Button(
                            "🔍 Search",
                            elem_classes=["btn-secondary"]
                        )
                        
                        search_output = gr.Textbox(
                            label="Search Results",
                            lines=15,
                            interactive=False,
                            elem_classes=["output-premium"]
                        )
            
            # AI Chat Tab
            with gr.TabItem("💬 AI Advisor"):
                with gr.Row():
                    with gr.Column(scale=2, elem_classes=["glass-card"]):
                        gr.Markdown("### 🤖 AI Career Advisor")
                        gr.Markdown("*Conversations saved to your history*")
                        
                        chatbot = gr.Chatbot(
                            label="Career Consultation",
                            height=600
                        )
                        
                        with gr.Row():
                            msg = gr.Textbox(
                                label="Your Question",
                                placeholder="Ask about career topics",
                                lines=2,
                                scale=4,
                                elem_classes=["input-premium"]
                            )
                            
                            send_btn = gr.Button(
                                "Send",
                                scale=1,
                                elem_classes=["btn-premium"]
                            )
                        
                        clear_btn = gr.Button(
                            "Clear Chat",
                            elem_classes=["btn-secondary"]
                        )
                    
                    with gr.Column(scale=1, elem_classes=["glass-card"]):
                        gr.Markdown("### 💡 Database Features")
                        gr.HTML("""
                            <div style="color: rgba(255, 255, 255, 0.9); line-height: 1.6;">
                                <h4 style="color: #00C6FF; margin-bottom: 15px;">🗄️ Data Storage</h4>
                                <ul style="margin-bottom: 25px;">
                                    <li style="margin-bottom: 8px;">Resume history & versions</li>
                                    <li style="margin-bottom: 8px;">Cover letter library</li>
                                    <li style="margin-bottom: 8px;">Job application tracking</li>
                                    <li style="margin-bottom: 8px;">Skill assessments saved</li>
                                    <li style="margin-bottom: 8px;">Chat conversation history</li>
                                </ul>
                                
                                <h4 style="color: #00C6FF; margin-bottom: 15px;">📊 Analytics</h4>
                                <ul>
                                    <li style="margin-bottom: 8px;">Usage statistics</li>
                                    <li style="margin-bottom: 8px;">Document performance</li>
                                    <li style="margin-bottom: 8px;">Skill development tracking</li>
                                    <li style="margin-bottom: 8px;">Career progress metrics</li>
                                </ul>
                            </div>
                        """)
        
        # Connect enhanced functions
        generate_resume_btn.click(
            fn=enhanced_resume_generation,
            inputs=[resume_name, resume_role, resume_skills, resume_experience, resume_education],
            outputs=[resume_output, resume_pdf]
        )
        
        generate_cl_btn.click(
            fn=enhanced_cover_letter_generation,
            inputs=[cl_name, cl_role, cl_company, cl_skills],
            outputs=[cl_output, cl_pdf]
        )
        
        analyze_btn.click(
            fn=enhanced_resume_analysis,
            inputs=[analysis_upload],
            outputs=[analysis_output]
        )
        
        ats_btn.click(
            fn=enhanced_ats_calculation,
            inputs=[ats_upload, job_desc],
            outputs=[ats_output]
        )
        
        match_jobs_btn.click(
            fn=match_jobs_interface,
            inputs=[user_skills],
            outputs=[job_matches]
        )
        
        gap_analysis_btn.click(
            fn=enhanced_skill_gap_analysis,
            inputs=[current_skills, target_job],
            outputs=[gap_results]
        )
        
        history_btn.click(
            fn=get_user_history,
            inputs=[],
            outputs=[history_output]
        )
        
        search_btn.click(
            fn=search_user_documents,
            inputs=[search_input],
            outputs=[search_output]
        )
        
        send_btn.click(
            fn=enhanced_chatbot_interface,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            fn=enhanced_chatbot_interface,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        clear_btn.click(
            lambda: [],
            outputs=[chatbot]
        )
    
    return interface

if __name__ == "__main__":
    try:
        app = create_database_enhanced_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=5000,
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
    except Exception as e:
        print(f"Error: Failed to start the database-enhanced application - {e}")