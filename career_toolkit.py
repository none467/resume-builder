import gradio as gr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import pdfplumber
import tempfile
import logging
import re
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import json

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

class ComprehensiveCareerToolkit:
    def __init__(self):
        """Initialize the Comprehensive Career Toolkit."""
        self.model_name = "microsoft/phi-1_5"
        self.tokenizer = None
        self.model = None
        self.ai_enabled = AI_AVAILABLE
        self.job_database = self.create_job_database()
        self.skills_database = self.create_skills_database()
        
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
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.ai_enabled = False
            logger.info("Switching to fallback mode")
    
    def create_job_database(self):
        """Create a comprehensive job database with skills requirements."""
        jobs_data = {
            'Software Engineer': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git', 'Docker', 'AWS', 'API Development', 'Testing'],
            'Data Scientist': ['Python', 'R', 'Machine Learning', 'SQL', 'Statistics', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'Data Visualization'],
            'Product Manager': ['Product Strategy', 'Market Research', 'Agile', 'Roadmapping', 'Analytics', 'User Research', 'A/B Testing', 'Communication', 'Leadership'],
            'Digital Marketing Manager': ['SEO', 'SEM', 'Google Analytics', 'Social Media Marketing', 'Content Strategy', 'Email Marketing', 'PPC', 'Marketing Automation'],
            'UX/UI Designer': ['Figma', 'Adobe Creative Suite', 'User Research', 'Wireframing', 'Prototyping', 'Design Systems', 'Usability Testing', 'HTML/CSS'],
            'DevOps Engineer': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform', 'Jenkins', 'Monitoring', 'Scripting', 'Cloud Infrastructure'],
            'Financial Analyst': ['Excel', 'Financial Modeling', 'SQL', 'Python', 'Tableau', 'Financial Reporting', 'Valuation', 'Risk Analysis', 'Budgeting'],
            'Business Analyst': ['Requirements Analysis', 'Process Mapping', 'SQL', 'Tableau', 'Stakeholder Management', 'Documentation', 'Agile', 'Data Analysis'],
            'Sales Manager': ['CRM', 'Lead Generation', 'Sales Strategy', 'Negotiation', 'Pipeline Management', 'Customer Relationship Management', 'Forecasting'],
            'HR Manager': ['Recruitment', 'Employee Relations', 'Performance Management', 'HRIS', 'Compliance', 'Training Development', 'Compensation'],
            'Cybersecurity Analyst': ['Network Security', 'Penetration Testing', 'SIEM', 'Incident Response', 'Risk Assessment', 'Compliance', 'Firewalls'],
            'Machine Learning Engineer': ['Python', 'TensorFlow', 'PyTorch', 'MLOps', 'Docker', 'Kubernetes', 'Model Deployment', 'Feature Engineering'],
            'Content Writer': ['SEO Writing', 'Content Strategy', 'Copywriting', 'WordPress', 'Social Media', 'Research', 'Grammar', 'Content Management'],
            'Project Manager': ['PMP', 'Agile', 'Scrum', 'Risk Management', 'Budget Management', 'Stakeholder Management', 'Communication', 'Leadership'],
            'Quality Assurance Engineer': ['Test Automation', 'Selenium', 'API Testing', 'Manual Testing', 'Bug Tracking', 'Test Planning', 'Performance Testing']
        }
        return jobs_data
    
    def create_skills_database(self):
        """Create a database of skills with learning resources."""
        skills_data = {
            'Python': {'category': 'Programming', 'difficulty': 'Medium', 'resources': ['Codecademy Python Course', 'Python.org Tutorial', 'Automate the Boring Stuff']},
            'JavaScript': {'category': 'Programming', 'difficulty': 'Medium', 'resources': ['MDN Web Docs', 'JavaScript.info', 'FreeCodeCamp']},
            'Machine Learning': {'category': 'Data Science', 'difficulty': 'Hard', 'resources': ['Coursera ML Course', 'Kaggle Learn', 'Scikit-learn Documentation']},
            'React': {'category': 'Frontend', 'difficulty': 'Medium', 'resources': ['React Official Docs', 'React Tutorial', 'FreeCodeCamp React']},
            'SQL': {'category': 'Database', 'difficulty': 'Easy', 'resources': ['W3Schools SQL', 'SQLBolt', 'Codecademy SQL']},
            'AWS': {'category': 'Cloud', 'difficulty': 'Hard', 'resources': ['AWS Training', 'A Cloud Guru', 'AWS Documentation']},
            'Docker': {'category': 'DevOps', 'difficulty': 'Medium', 'resources': ['Docker Official Tutorial', 'Docker Mastery Course', 'Play with Docker']},
            'Data Visualization': {'category': 'Data Science', 'difficulty': 'Medium', 'resources': ['Tableau Public Training', 'D3.js Tutorial', 'Matplotlib Documentation']},
            'Project Management': {'category': 'Management', 'difficulty': 'Medium', 'resources': ['PMI Resources', 'Coursera Project Management', 'Scrum.org']},
            'SEO': {'category': 'Marketing', 'difficulty': 'Medium', 'resources': ['Google SEO Starter Guide', 'Moz SEO Learning Center', 'SEMrush Academy']}
        }
        return skills_data

    # Resume Generation (Enhanced from existing)
    def generate_resume_content(self, name, job_role, skills, experience, education):
        """Generate resume content using intelligent structured approach."""
        if not self.ai_enabled or self.model is None or self.tokenizer is None:
            return self.create_intelligent_resume(name, job_role, skills, experience, education)
            
        try:
            prompt = f"""Generate a professional resume content for the following person:

Name: {name}
Job Role: {job_role}
Skills: {skills}
Experience: {experience}
Education: {education}

Create a well-structured professional resume with sections:
1. Professional Summary
2. Skills
3. Work Experience
4. Education
5. Additional qualifications

Make it professional, concise, and tailored for the {job_role} position."""

            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
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
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            resume_content = generated_text[len(prompt):].strip()
            
            if len(resume_content) < 100:
                resume_content = self.create_intelligent_resume(name, job_role, skills, experience, education)
            
            return resume_content
            
        except Exception as e:
            logger.error(f"Error generating resume content: {e}")
            return self.create_intelligent_resume(name, job_role, skills, experience, education)

    def create_intelligent_resume(self, name, job_role, skills, experience, education):
        """Create an intelligent structured resume with dynamic content."""
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        formatted_skills = '\n'.join([f"• {skill}" for skill in skills_list])
        
        summary = self.generate_summary(job_role, skills_list)
        formatted_experience = self.format_experience(experience)
        formatted_education = self.format_education(education)
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
        
        relevant_keywords = []
        for key, keywords in role_keywords.items():
            if key.lower() in job_role.lower():
                relevant_keywords.extend(keywords)
        
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
        
        experiences = re.split(r'[.]\s*(?=[A-Z])|[\n]+', experience)
        formatted_exp = []
        
        for exp in experiences:
            exp = exp.strip()
            if len(exp) > 10:
                if not exp.endswith('.'):
                    exp += '.'
                formatted_exp.append(f"• {exp}")
        
        return '\n'.join(formatted_exp) if formatted_exp else experience
    
    def format_education(self, education):
        """Format the education section with better structure."""
        if not education.strip():
            return "Please add your educational background."
        
        edu_items = re.split(r'[.]\s*(?=[A-Z])|[\n]+', education)
        formatted_edu = []
        
        for item in edu_items:
            item = item.strip()
            if len(item) > 5:
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
        
        achievements = []
        for key, achievs in role_achievements.items():
            if key.lower() in job_role.lower():
                achievements.extend(achievs)
                break
        
        if not achievements:
            achievements = [
                "Strong problem-solving and analytical abilities",
                "Excellent communication and collaboration skills",
                "Adaptable to new technologies and methodologies",
                "Detail-oriented with strong organizational capabilities"
            ]
        
        return '\n'.join([f"• {achievement}" for achievement in achievements])

    # Cover Letter Generation (Enhanced from existing)
    def generate_cover_letter_content(self, name, job_role, company, skills):
        """Generate cover letter content using intelligent structured approach."""
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        top_skills = skills_list[:4] if len(skills_list) >= 4 else skills_list
        
        opening = self.generate_cover_letter_opening(job_role, company)
        body = self.generate_cover_letter_body(job_role, top_skills, company)
        closing = self.generate_cover_letter_closing(company)
        
        cover_letter_content = f"""
COVER LETTER

{name}
{job_role} Application

Date: {datetime.now().strftime("%B %d, %Y")}

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
        
        role_content = {
            'software': f"My technical expertise in {skills_text} aligns perfectly with the requirements for this role. I have successfully developed and deployed applications that have improved user experience and system performance. My passion for clean, efficient code and collaborative development makes me an ideal fit for {company}'s technical team.",
            'engineer': f"With my strong foundation in {skills_text}, I bring both technical proficiency and problem-solving capabilities to this role. My experience in project execution and technical documentation, combined with my commitment to engineering excellence, positions me well to contribute to {company}'s innovative projects.",
            'manager': f"My leadership experience and skills in {skills_text} have enabled me to successfully guide teams and deliver results. I excel at strategic planning, team development, and cross-functional collaboration. I am confident that my management approach and vision align with {company}'s leadership values.",
            'marketing': f"My expertise in {skills_text} has driven successful campaigns and brand growth throughout my career. I understand the importance of data-driven decision making and creative strategy execution. I am excited about the opportunity to bring my marketing insights and innovative approach to {company}.",
            'data': f"My analytical skills and proficiency in {skills_text} have enabled me to extract meaningful insights from complex datasets. I excel at translating data into actionable business strategies and presenting findings to stakeholders. I am eager to apply my data expertise to help {company} make informed decisions.",
            'design': f"My design philosophy centers on user-centered solutions, supported by my skills in {skills_text}. I have successfully created intuitive interfaces and compelling visual experiences that enhance user engagement. I am excited to contribute my creative vision and technical skills to {company}'s design initiatives.",
            'sales': f"My sales experience and skills in {skills_text} have consistently resulted in exceeding targets and building strong client relationships. I understand the importance of consultative selling and customer satisfaction. I am confident that my proven track record and relationship-building abilities will contribute to {company}'s continued growth."
        }
        
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

    # Resume Analyzer
    def analyze_resume(self, resume_file):
        """Analyze uploaded resume and provide improvement suggestions."""
        if resume_file is None:
            return "Please upload a resume file to analyze.", None, None
        
        try:
            # Extract text from PDF
            resume_text = self.extract_text_from_pdf(resume_file.name)
            
            if not resume_text or len(resume_text.strip()) < 50:
                return "Could not extract sufficient text from the resume. Please ensure the PDF contains readable text.", None, None
            
            # Analyze resume sections
            analysis = self.perform_resume_analysis(resume_text)
            
            # Generate improvement suggestions
            suggestions = self.generate_improvement_suggestions(analysis)
            
            # Create analysis report
            report = self.create_analysis_report(analysis, suggestions)
            
            return report, None, None
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            return f"Error analyzing resume: {str(e)}", None, None
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using pdfplumber."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def perform_resume_analysis(self, resume_text):
        """Perform comprehensive resume analysis."""
        analysis = {
            'sections_found': [],
            'sections_missing': [],
            'word_count': len(resume_text.split()),
            'skills_found': [],
            'contact_info': False,
            'action_verbs': 0,
            'quantified_achievements': 0,
            'grammar_issues': []
        }
        
        # Check for required sections
        required_sections = ['experience', 'education', 'skills', 'summary', 'objective']
        text_lower = resume_text.lower()
        
        for section in required_sections:
            if section in text_lower or (section == 'summary' and 'profile' in text_lower):
                analysis['sections_found'].append(section.title())
            else:
                analysis['sections_missing'].append(section.title())
        
        # Check for contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        if re.search(email_pattern, resume_text) or re.search(phone_pattern, resume_text):
            analysis['contact_info'] = True
        
        # Find skills mentioned
        all_skills = set()
        for job_skills in self.job_database.values():
            all_skills.update([skill.lower() for skill in job_skills])
        
        for skill in all_skills:
            if skill.lower() in text_lower:
                analysis['skills_found'].append(skill.title())
        
        # Count action verbs
        action_verbs = ['managed', 'developed', 'created', 'implemented', 'designed', 'led', 'improved', 'increased', 'reduced', 'achieved', 'delivered', 'built', 'established', 'coordinated', 'analyzed']
        for verb in action_verbs:
            analysis['action_verbs'] += len(re.findall(r'\b' + verb + r'\w*\b', text_lower))
        
        # Count quantified achievements (numbers + %)
        number_pattern = r'\b\d+(?:\.\d+)?%?\b'
        analysis['quantified_achievements'] = len(re.findall(number_pattern, resume_text))
        
        # Basic grammar check (simplified)
        grammar_issues = []
        if resume_text.count('.') < 5:
            grammar_issues.append("Consider adding more complete sentences")
        if resume_text.count(',') < 3:
            grammar_issues.append("Consider using more comma-separated lists for clarity")
        
        analysis['grammar_issues'] = grammar_issues
        
        return analysis
    
    def generate_improvement_suggestions(self, analysis):
        """Generate specific improvement suggestions based on analysis."""
        suggestions = []
        
        # Section completeness
        if len(analysis['sections_missing']) > 0:
            suggestions.append(f"Add missing sections: {', '.join(analysis['sections_missing'])}")
        
        # Word count
        if analysis['word_count'] < 200:
            suggestions.append("Resume is too short. Aim for 300-500 words with more detailed descriptions")
        elif analysis['word_count'] > 800:
            suggestions.append("Resume is too long. Consider condensing to 500-700 words")
        
        # Contact information
        if not analysis['contact_info']:
            suggestions.append("Add contact information (email and phone number)")
        
        # Skills
        if len(analysis['skills_found']) < 5:
            suggestions.append("Include more relevant technical and soft skills")
        
        # Action verbs
        if analysis['action_verbs'] < 5:
            suggestions.append("Use more action verbs to describe your achievements (managed, developed, created, etc.)")
        
        # Quantified achievements
        if analysis['quantified_achievements'] < 3:
            suggestions.append("Add more quantified achievements with specific numbers and percentages")
        
        # Grammar
        if analysis['grammar_issues']:
            suggestions.extend(analysis['grammar_issues'])
        
        return suggestions
    
    def create_analysis_report(self, analysis, suggestions):
        """Create a detailed analysis report."""
        report = f"""
RESUME ANALYSIS REPORT
======================

SECTIONS ANALYSIS:
✓ Found: {', '.join(analysis['sections_found']) if analysis['sections_found'] else 'None'}
⚠ Missing: {', '.join(analysis['sections_missing']) if analysis['sections_missing'] else 'None'}

CONTENT METRICS:
• Word Count: {analysis['word_count']} words
• Skills Identified: {len(analysis['skills_found'])} ({', '.join(analysis['skills_found'][:10])}{'...' if len(analysis['skills_found']) > 10 else ''})
• Action Verbs Used: {analysis['action_verbs']}
• Quantified Achievements: {analysis['quantified_achievements']}
• Contact Info Present: {'Yes' if analysis['contact_info'] else 'No'}

IMPROVEMENT SUGGESTIONS:
{chr(10).join([f"• {suggestion}" for suggestion in suggestions]) if suggestions else "• Your resume looks good overall!"}

OVERALL SCORE: {self.calculate_resume_score(analysis)}/100
"""
        return report
    
    def calculate_resume_score(self, analysis):
        """Calculate an overall resume score out of 100."""
        score = 0
        
        # Sections (40 points max)
        required_sections = 5
        found_sections = len(analysis['sections_found'])
        score += min(40, (found_sections / required_sections) * 40)
        
        # Word count (20 points max)
        if 300 <= analysis['word_count'] <= 700:
            score += 20
        elif 200 <= analysis['word_count'] <= 800:
            score += 15
        else:
            score += 10
        
        # Skills (15 points max)
        score += min(15, len(analysis['skills_found']) * 2)
        
        # Action verbs (10 points max)
        score += min(10, analysis['action_verbs'] * 1.5)
        
        # Quantified achievements (10 points max)
        score += min(10, analysis['quantified_achievements'] * 2)
        
        # Contact info (5 points max)
        if analysis['contact_info']:
            score += 5
        
        return int(min(100, score))

    # ATS Match Score Calculator
    def calculate_ats_score(self, resume_file, job_description):
        """Calculate ATS match score between resume and job description."""
        if resume_file is None or not job_description.strip():
            return "Please upload a resume file and provide a job description.", None
        
        try:
            # Extract resume text
            resume_text = self.extract_text_from_pdf(resume_file.name)
            
            if not resume_text:
                return "Could not extract text from resume file.", None
            
            # Calculate similarity using TF-IDF and cosine similarity
            documents = [resume_text, job_description]
            
            # Vectorize the documents
            vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            ats_score = similarity_matrix[0, 1] * 100
            
            # Extract keywords from job description
            job_keywords = self.extract_keywords(job_description)
            resume_keywords = self.extract_keywords(resume_text)
            
            # Find matching and missing keywords
            matching_keywords = set(job_keywords) & set(resume_keywords)
            missing_keywords = set(job_keywords) - set(resume_keywords)
            
            # Create detailed report
            report = self.create_ats_report(ats_score, matching_keywords, missing_keywords, job_keywords, resume_keywords)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error calculating ATS score: {e}")
            return f"Error calculating ATS score: {str(e)}", None
    
    def extract_keywords(self, text):
        """Extract important keywords from text."""
        # Simple keyword extraction using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english', max_features=50, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get TF-IDF scores
        scores = tfidf_matrix.toarray()[0]
        
        # Get top keywords
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [keyword for keyword, score in keyword_scores[:20] if score > 0.1]
    
    def create_ats_report(self, ats_score, matching_keywords, missing_keywords, job_keywords, resume_keywords):
        """Create detailed ATS analysis report."""
        score_level = "Excellent" if ats_score >= 80 else "Good" if ats_score >= 60 else "Fair" if ats_score >= 40 else "Needs Improvement"
        
        report = f"""
ATS MATCH SCORE ANALYSIS
========================

OVERALL ATS SCORE: {ats_score:.1f}% ({score_level})

KEYWORD ANALYSIS:
• Job Description Keywords: {len(job_keywords)}
• Resume Keywords Found: {len(matching_keywords)}
• Match Rate: {(len(matching_keywords) / len(job_keywords) * 100):.1f}%

MATCHING KEYWORDS ({len(matching_keywords)}):
{', '.join(list(matching_keywords)[:15])}{'...' if len(matching_keywords) > 15 else ''}

MISSING KEYWORDS ({len(missing_keywords)}):
{', '.join(list(missing_keywords)[:15])}{'...' if len(missing_keywords) > 15 else ''}

RECOMMENDATIONS:
• {'Excellent match! Your resume aligns well with the job requirements.' if ats_score >= 80 else 'Consider incorporating more of the missing keywords naturally into your resume.'}
• {'Focus on the missing keywords that are most relevant to your experience.' if missing_keywords else 'Great keyword coverage!'}
• {'Use variations of important keywords throughout your resume.' if ats_score < 60 else 'Maintain current keyword density.'}
"""
        return report

    # Job Matcher
    def match_jobs(self, user_skills):
        """Match user skills to available jobs in database."""
        if not user_skills.strip():
            return "Please enter your skills to find matching jobs.", None
        
        try:
            user_skills_list = [skill.strip().lower() for skill in user_skills.split(',')]
            job_matches = []
            
            for job_title, job_skills in self.job_database.items():
                job_skills_lower = [skill.lower() for skill in job_skills]
                
                # Calculate match percentage
                matching_skills = set(user_skills_list) & set(job_skills_lower)
                match_percentage = (len(matching_skills) / len(job_skills_lower)) * 100
                
                if match_percentage > 0:
                    job_matches.append({
                        'job_title': job_title,
                        'match_percentage': match_percentage,
                        'matching_skills': list(matching_skills),
                        'missing_skills': list(set(job_skills_lower) - set(user_skills_list))
                    })
            
            # Sort by match percentage
            job_matches.sort(key=lambda x: x['match_percentage'], reverse=True)
            
            # Create report
            report = self.create_job_match_report(job_matches[:5], user_skills_list)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error matching jobs: {e}")
            return f"Error matching jobs: {str(e)}", None
    
    def create_job_match_report(self, job_matches, user_skills):
        """Create job matching report."""
        if not job_matches:
            return "No matching jobs found. Consider expanding your skillset or trying different skill keywords."
        
        report = f"""
JOB MATCHING ANALYSIS
=====================

YOUR SKILLS: {', '.join(user_skills)}

TOP 5 MATCHING JOBS:

"""
        
        for i, match in enumerate(job_matches, 1):
            report += f"""
{i}. {match['job_title']} - {match['match_percentage']:.1f}% Match
   ✓ Matching Skills: {', '.join(match['matching_skills'][:5])}{'...' if len(match['matching_skills']) > 5 else ''}
   ⚠ Skills to Develop: {', '.join(match['missing_skills'][:3])}{'...' if len(match['missing_skills']) > 3 else ''}

"""
        
        return report

    # Resume Perfection Score
    def calculate_perfection_score(self, resume_file):
        """Calculate comprehensive resume perfection score."""
        if resume_file is None:
            return "Please upload a resume file to calculate the perfection score.", None
        
        try:
            resume_text = self.extract_text_from_pdf(resume_file.name)
            if not resume_text:
                return "Could not extract text from resume file.", None
            
            # Perform detailed analysis
            analysis = self.perform_resume_analysis(resume_text)
            
            # Calculate detailed scores
            scores = self.calculate_detailed_scores(analysis, resume_text)
            
            # Generate improvement recommendations
            recommendations = self.generate_detailed_recommendations(scores, analysis)
            
            # Create perfection score report
            report = self.create_perfection_score_report(scores, recommendations)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error calculating perfection score: {e}")
            return f"Error calculating perfection score: {str(e)}", None
    
    def calculate_detailed_scores(self, analysis, resume_text):
        """Calculate detailed scoring metrics."""
        scores = {
            'structure': 0,
            'content': 0,
            'keywords': 0,
            'formatting': 0,
            'grammar': 0,
            'overall': 0
        }
        
        # Structure Score (25 points)
        required_sections = ['experience', 'education', 'skills', 'summary']
        sections_found = len(analysis['sections_found'])
        scores['structure'] = min(25, (sections_found / len(required_sections)) * 25)
        
        # Content Score (25 points)
        content_score = 0
        if analysis['word_count'] >= 300:
            content_score += 5
        if analysis['action_verbs'] >= 5:
            content_score += 5
        if analysis['quantified_achievements'] >= 3:
            content_score += 5
        if len(analysis['skills_found']) >= 5:
            content_score += 5
        if analysis['contact_info']:
            content_score += 5
        scores['content'] = content_score
        
        # Keywords Score (20 points)
        scores['keywords'] = min(20, len(analysis['skills_found']) * 2)
        
        # Formatting Score (15 points)
        formatting_score = 15  # Assume good formatting for PDF
        if len(resume_text.split()) < 200:
            formatting_score -= 5
        scores['formatting'] = formatting_score
        
        # Grammar Score (15 points)
        grammar_score = 15 - len(analysis['grammar_issues']) * 3
        scores['grammar'] = max(0, grammar_score)
        
        # Calculate overall score
        scores['overall'] = sum(scores.values()) - scores['overall']  # Exclude overall from sum
        
        return scores
    
    def generate_detailed_recommendations(self, scores, analysis):
        """Generate detailed recommendations for improvement."""
        recommendations = []
        
        if scores['structure'] < 20:
            recommendations.append("Improve resume structure by adding missing sections")
        
        if scores['content'] < 20:
            recommendations.append("Enhance content with more action verbs and quantified achievements")
        
        if scores['keywords'] < 15:
            recommendations.append("Include more relevant industry keywords and technical skills")
        
        if scores['formatting'] < 12:
            recommendations.append("Improve formatting and ensure consistent styling")
        
        if scores['grammar'] < 12:
            recommendations.append("Review grammar and sentence structure")
        
        return recommendations
    
    def create_perfection_score_report(self, scores, recommendations):
        """Create comprehensive perfection score report."""
        overall_score = scores['overall']
        grade = "A+" if overall_score >= 90 else "A" if overall_score >= 80 else "B+" if overall_score >= 70 else "B" if overall_score >= 60 else "C"
        
        report = f"""
RESUME PERFECTION SCORE
=======================

OVERALL SCORE: {overall_score}/100 (Grade: {grade})

DETAILED BREAKDOWN:
• Structure & Sections: {scores['structure']}/25
• Content Quality: {scores['content']}/25  
• Keywords & Skills: {scores['keywords']}/20
• Formatting: {scores['formatting']}/15
• Grammar & Language: {scores['grammar']}/15

RECOMMENDATIONS FOR IMPROVEMENT:
{chr(10).join([f"• {rec}" for rec in recommendations]) if recommendations else "• Excellent work! Your resume is well-optimized."}

NEXT STEPS:
• {"Focus on the lowest-scoring areas first" if recommendations else "Consider customizing for specific job applications"}
• {"Use action verbs and quantify achievements" if scores['content'] < 20 else "Maintain current high content quality"}
• {"Research industry-specific keywords" if scores['keywords'] < 15 else "Keep keywords updated with industry trends"}
"""
        return report

    # LinkedIn Summary Generator
    def generate_linkedin_summary(self, name, job_role, skills, experience):
        """Generate professional LinkedIn summary."""
        if not all([name.strip(), job_role.strip(), skills.strip()]):
            return "Please fill in name, job role, and skills to generate LinkedIn summary.", None
        
        try:
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            top_skills = skills_list[:5]
            
            # Generate professional summary
            summary = self.create_linkedin_summary_content(name, job_role, top_skills, experience)
            
            return summary, None
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn summary: {e}")
            return f"Error generating LinkedIn summary: {str(e)}", None
    
    def create_linkedin_summary_content(self, name, job_role, skills, experience):
        """Create LinkedIn summary content."""
        skills_text = " | ".join(skills)
        
        # Create engaging opening
        opening_templates = {
            'software': f"Passionate {job_role} dedicated to crafting innovative solutions that drive business growth",
            'data': f"Data-driven {job_role} who transforms complex information into actionable business insights",
            'marketing': f"Creative {job_role} with a proven track record of building brands and driving engagement",
            'manager': f"Results-oriented {job_role} who empowers teams to exceed goals and deliver exceptional outcomes",
            'design': f"User-focused {job_role} passionate about creating intuitive experiences that delight users"
        }
        
        opening = opening_templates.get('software', f"Experienced {job_role} committed to excellence and continuous innovation")
        for key in opening_templates:
            if key in job_role.lower():
                opening = opening_templates[key]
                break
        
        # Create experience highlight
        experience_highlight = ""
        if experience and len(experience.strip()) > 20:
            experience_highlight = f"\n\n🏆 Professional Highlights:\n{self.format_experience_for_linkedin(experience)}"
        
        summary = f"""
{opening}. Specializing in {skills_text}.

💼 What I Bring:
• Deep expertise in {skills[0] if skills else 'my field'} with hands-on experience in {skills[1] if len(skills) > 1 else 'various technologies'}
• Strong problem-solving abilities and analytical thinking
• Collaborative approach to achieving team and organizational goals
• Continuous learning mindset to stay current with industry trends
{experience_highlight}

🎯 I'm passionate about leveraging technology and innovation to solve real-world challenges and create meaningful impact.

📫 Let's connect! I'm always open to discussing opportunities, sharing insights, or collaborating on interesting projects.

#OpenToWork #{job_role.replace(' ', '')} #{skills[0].replace(' ', '') if skills else 'Technology'}
"""
        return summary.strip()
    
    def format_experience_for_linkedin(self, experience):
        """Format experience for LinkedIn summary."""
        # Extract key achievements
        sentences = experience.split('.')
        highlights = []
        
        for sentence in sentences[:3]:  # Take first 3 meaningful sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and any(word in sentence.lower() for word in ['developed', 'managed', 'led', 'created', 'improved', 'increased']):
                highlights.append(f"• {sentence.capitalize()}")
        
        return '\n'.join(highlights) if highlights else "• Proven track record of delivering results and exceeding expectations"

    # Skill Gap Finder
    def find_skill_gaps(self, current_skills, target_job):
        """Find skill gaps for target job role."""
        if not current_skills.strip() or not target_job.strip():
            return "Please enter your current skills and target job role.", None
        
        try:
            current_skills_list = [skill.strip().lower() for skill in current_skills.split(',')]
            
            # Find target job requirements
            target_job_skills = None
            for job_title, job_skills in self.job_database.items():
                if target_job.lower() in job_title.lower():
                    target_job_skills = [skill.lower() for skill in job_skills]
                    break
            
            if not target_job_skills:
                # Find partial matches
                for job_title, job_skills in self.job_database.items():
                    if any(word in job_title.lower() for word in target_job.lower().split()):
                        target_job_skills = [skill.lower() for skill in job_skills]
                        break
            
            if not target_job_skills:
                return f"Job role '{target_job}' not found in database. Try: {', '.join(list(self.job_database.keys())[:5])}", None
            
            # Calculate gaps
            matching_skills = set(current_skills_list) & set(target_job_skills)
            missing_skills = set(target_job_skills) - set(current_skills_list)
            
            # Generate learning roadmap
            roadmap = self.create_learning_roadmap(missing_skills)
            
            # Create skill gap report
            report = self.create_skill_gap_report(target_job, matching_skills, missing_skills, roadmap, current_skills_list, target_job_skills)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error finding skill gaps: {e}")
            return f"Error finding skill gaps: {str(e)}", None
    
    def create_learning_roadmap(self, missing_skills):
        """Create learning roadmap for missing skills."""
        roadmap = {}
        
        for skill in missing_skills:
            skill_title = skill.title()
            if skill in self.skills_database:
                roadmap[skill_title] = self.skills_database[skill]
            else:
                # Default learning path
                roadmap[skill_title] = {
                    'category': 'General',
                    'difficulty': 'Medium',
                    'resources': ['Online tutorials', 'Documentation', 'Practice projects']
                }
        
        return roadmap
    
    def create_skill_gap_report(self, target_job, matching_skills, missing_skills, roadmap, current_skills, target_skills):
        """Create comprehensive skill gap analysis report."""
        match_percentage = (len(matching_skills) / len(target_skills)) * 100
        
        report = f"""
SKILL GAP ANALYSIS
==================

TARGET ROLE: {target_job.title()}
SKILL MATCH: {match_percentage:.1f}% ({len(matching_skills)}/{len(target_skills)} skills)

✅ SKILLS YOU HAVE ({len(matching_skills)}):
{', '.join([skill.title() for skill in matching_skills]) if matching_skills else 'None identified'}

⚠️ SKILLS TO DEVELOP ({len(missing_skills)}):
{', '.join([skill.title() for skill in missing_skills]) if missing_skills else 'None - you have all required skills!'}

📚 LEARNING ROADMAP:
"""
        
        if roadmap:
            for skill, info in list(roadmap.items())[:5]:  # Show top 5
                report += f"""
{skill} ({info['difficulty']} difficulty)
• Category: {info['category']}
• Resources: {', '.join(info['resources'][:2])}
"""
        else:
            report += "\n🎉 Congratulations! You already have all the required skills for this role."
        
        report += f"""

🎯 RECOMMENDED NEXT STEPS:
• {"Focus on developing the missing skills listed above" if missing_skills else "Consider advanced certifications in your existing skills"}
• {"Start with easier skills and build up to more complex ones" if any(info['difficulty'] == 'Hard' for info in roadmap.values()) else "Practice through hands-on projects"}
• {"Update your resume to highlight matching skills" if matching_skills else "Consider related roles that better match your skillset"}

READINESS LEVEL: {self.calculate_readiness_level(match_percentage)}
"""
        
        return report
    
    def calculate_readiness_level(self, match_percentage):
        """Calculate job readiness level."""
        if match_percentage >= 80:
            return "Ready to Apply! 🚀"
        elif match_percentage >= 60:
            return "Almost Ready - 1-2 skills needed 💪"
        elif match_percentage >= 40:
            return "Developing - Focus on key skills 📈"
        else:
            return "Early Stage - Significant development needed 📚"

    # Career Insights Dashboard
    def create_career_dashboard(self, resume_file, skills, target_job):
        """Create comprehensive career insights dashboard."""
        if not skills.strip():
            return "Please enter your skills to generate career insights.", None, None
        
        try:
            insights = {}
            
            # Calculate various metrics
            if resume_file:
                resume_text = self.extract_text_from_pdf(resume_file.name)
                if resume_text:
                    analysis = self.perform_resume_analysis(resume_text)
                    insights['resume_score'] = self.calculate_resume_score(analysis)
                else:
                    insights['resume_score'] = 0
            else:
                insights['resume_score'] = 0
            
            # Job match analysis
            if target_job:
                job_match_result = self.match_jobs(skills)
                # Extract match percentage for target job
                insights['job_match'] = self.extract_job_match_percentage(job_match_result[0], target_job)
            else:
                insights['job_match'] = 0
            
            # Skill analysis
            user_skills_list = [skill.strip() for skill in skills.split(',')]
            insights['skill_count'] = len(user_skills_list)
            insights['skills'] = user_skills_list
            
            # Generate visualizations
            dashboard_plots = self.create_dashboard_visualizations(insights)
            
            # Create summary report
            summary = self.create_career_summary(insights, target_job)
            
            return summary, dashboard_plots, None
            
        except Exception as e:
            logger.error(f"Error creating career dashboard: {e}")
            return f"Error creating career dashboard: {str(e)}", None, None
    
    def extract_job_match_percentage(self, job_match_text, target_job):
        """Extract job match percentage from job match results."""
        if not job_match_text or not target_job:
            return 0
        
        lines = job_match_text.split('\n')
        for line in lines:
            if target_job.lower() in line.lower() and '% Match' in line:
                match = re.search(r'(\d+\.\d+)% Match', line)
                if match:
                    return float(match.group(1))
        
        # If specific job not found, return average of top matches
        matches = re.findall(r'(\d+\.\d+)% Match', job_match_text)
        if matches:
            return sum(float(match) for match in matches[:3]) / len(matches[:3])
        
        return 0
    
    def create_dashboard_visualizations(self, insights):
        """Create visualization plots for career dashboard."""
        try:
            # Create a skills distribution pie chart
            fig = plt.figure(figsize=(12, 8))
            
            # Subplot 1: Career Readiness Gauge
            ax1 = plt.subplot(2, 2, 1)
            categories = ['Resume Score', 'Job Match', 'Skill Count (x10)']
            values = [insights['resume_score'], insights['job_match'], min(100, insights['skill_count'] * 10)]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            bars = ax1.bar(categories, values, color=colors)
            ax1.set_title('Career Readiness Metrics', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Score')
            ax1.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                        f'{value:.1f}', ha='center', va='bottom')
            
            # Subplot 2: Skills Category Distribution (if we had categories)
            ax2 = plt.subplot(2, 2, 2)
            skill_categories = {}
            for skill in insights['skills'][:8]:  # Top 8 skills
                category = 'Technical'  # Simplified categorization
                if any(word in skill.lower() for word in ['management', 'leadership', 'communication']):
                    category = 'Soft Skills'
                elif any(word in skill.lower() for word in ['design', 'creative', 'ui', 'ux']):
                    category = 'Design'
                
                skill_categories[category] = skill_categories.get(category, 0) + 1
            
            if skill_categories:
                ax2.pie(skill_categories.values(), labels=skill_categories.keys(), 
                       autopct='%1.1f%%', startangle=90, colors=['#FF9999', '#66B2FF', '#99FF99'])
                ax2.set_title('Skills Distribution', fontsize=14, fontweight='bold')
            
            # Subplot 3: Career Progress Timeline
            ax3 = plt.subplot(2, 1, 2)
            milestones = ['Current State', 'Resume Optimized', 'Skills Developed', 'Job Ready']
            progress = [
                insights['resume_score'] * 0.5,  # Current
                min(100, insights['resume_score'] + 20),  # After resume optimization
                min(100, insights['job_match'] + 30),  # After skill development
                min(100, (insights['resume_score'] + insights['job_match']) / 2 + 25)  # Job ready
            ]
            
            ax3.plot(milestones, progress, marker='o', linewidth=3, markersize=8, color='#4ECDC4')
            ax3.fill_between(milestones, progress, alpha=0.3, color='#4ECDC4')
            ax3.set_title('Career Development Roadmap', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Readiness Score')
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save plot to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png", prefix="career_dashboard_")
            plt.savefig(temp_file.name, dpi=300, bbox_inches='tight')
            plt.close()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating dashboard visualizations: {e}")
            return None
    
    def create_career_summary(self, insights, target_job):
        """Create career insights summary."""
        readiness_score = (insights['resume_score'] + insights['job_match']) / 2
        readiness_level = self.calculate_readiness_level(readiness_score)
        
        summary = f"""
CAREER INSIGHTS DASHBOARD
=========================

🎯 TARGET ROLE: {target_job.title() if target_job else 'Not specified'}

📊 KEY METRICS:
• Resume Quality Score: {insights['resume_score']}/100
• Job Match Score: {insights['job_match']:.1f}%
• Skills Portfolio: {insights['skill_count']} skills identified
• Overall Readiness: {readiness_score:.1f}/100

🚀 CAREER READINESS: {readiness_level}

💡 INSIGHTS & RECOMMENDATIONS:

Resume Optimization:
• {"Excellent resume quality!" if insights['resume_score'] >= 80 else "Focus on improving resume structure and content"}
• {"Continue maintaining high standards" if insights['resume_score'] >= 80 else "Add more quantified achievements and relevant keywords"}

Skill Development:
• {"Strong skill portfolio!" if insights['skill_count'] >= 8 else "Consider expanding your skillset"}
• {"Focus on depth in key areas" if insights['skill_count'] >= 10 else "Add both technical and soft skills"}

Job Market Positioning:
• {"Excellent match with target role!" if insights['job_match'] >= 80 else "Develop missing skills for better job fit"}
• {"Ready to apply for senior positions" if readiness_score >= 75 else "Consider entry to mid-level positions"}

🎯 NEXT STEPS:
1. {"Apply for positions - you're ready!" if readiness_score >= 80 else "Focus on highest-impact improvements first"}
2. {"Network with industry professionals" if readiness_score >= 60 else "Complete online courses for missing skills"}
3. {"Prepare for technical interviews" if readiness_score >= 70 else "Build portfolio projects to demonstrate skills"}

📈 CAREER TRAJECTORY: {self.predict_career_trajectory(readiness_score, insights['skill_count'])}
"""
        return summary
    
    def predict_career_trajectory(self, readiness_score, skill_count):
        """Predict career trajectory based on current metrics."""
        if readiness_score >= 85 and skill_count >= 10:
            return "Senior/Lead positions within 6-12 months"
        elif readiness_score >= 70 and skill_count >= 8:
            return "Mid-level positions within 3-6 months"
        elif readiness_score >= 55 and skill_count >= 5:
            return "Entry to mid-level positions within 6-12 months"
        else:
            return "Focus on skill development for 6-12 months before applying"

    # PDF Creation Methods
    def create_pdf(self, content, name, doc_type="resume"):
        """Create a PDF from content using fpdf."""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            pdf.set_left_margin(20)
            pdf.set_right_margin(20)
            pdf.set_top_margin(20)
            
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(5)
                    continue
                
                # Header formatting
                if (line.isupper() and len(line) > 3) or any(keyword in line.upper() for keyword in ['SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'QUALIFICATIONS']):
                    pdf.set_font("Arial", 'B', 14)
                    pdf.ln(5)
                    pdf.cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    pdf.ln(2)
                    pdf.set_font("Arial", size=12)
                else:
                    # Text wrapping
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
            
            # Save PDF
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix=f"{name.replace(' ', '_')}_{doc_type}_")
            pdf.output(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            raise Exception(f"Failed to create PDF: {e}")
    
    def create_cover_letter_pdf(self, content, name, company):
        """Create a PDF from cover letter content."""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            pdf.set_left_margin(20)
            pdf.set_right_margin(20)
            pdf.set_top_margin(20)
            
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(3)
                    continue
                
                if line == "COVER LETTER":
                    pdf.set_font("Arial", 'B', 16)
                    pdf.ln(5)
                    pdf.cell(0, 12, line.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
                    pdf.ln(5)
                    pdf.set_font("Arial", size=12)
                elif "Application" in line or line.startswith("Date:") or line.startswith("Dear") or line.startswith("Sincerely"):
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    if line.startswith("Dear"):
                        pdf.ln(3)
                    pdf.set_font("Arial", size=12)
                else:
                    # Text wrapping for cover letters
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
                    
                    if len(line) > 50:
                        pdf.ln(2)
            
            company_clean = company.replace(' ', '_').replace('/', '_')
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", 
                                                   prefix=f"{name.replace(' ', '_')}_cover_letter_{company_clean}_")
            pdf.output(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating cover letter PDF: {e}")
            raise Exception(f"Failed to create cover letter PDF: {e}")

# Initialize the toolkit
toolkit = ComprehensiveCareerToolkit()

# Main functions for Gradio interface
def generate_resume(name, job_role, skills, experience, education):
    """Generate resume and create PDF."""
    try:
        if not all([name.strip(), job_role.strip(), skills.strip(), experience.strip(), education.strip()]):
            return "Error: Please fill in all fields to generate your resume.", None
        
        resume_content = toolkit.generate_resume_content(name, job_role, skills, experience, education)
        pdf_path = toolkit.create_pdf(resume_content, name, "resume")
        
        return f"Resume generated successfully for {name}!\n\n{resume_content[:500]}...", pdf_path
        
    except Exception as e:
        logger.error(f"Error in generate_resume: {e}")
        return f"Error generating resume: {str(e)}", None

def generate_cover_letter(name, job_role, company, skills):
    """Generate cover letter and create PDF."""
    try:
        if not all([name.strip(), job_role.strip(), company.strip(), skills.strip()]):
            return "Error: Please fill in all fields to generate your cover letter.", None
        
        cover_letter_content = toolkit.generate_cover_letter_content(name, job_role, company, skills)
        pdf_path = toolkit.create_cover_letter_pdf(cover_letter_content, name, company)
        
        return f"Cover letter generated successfully for {name} applying to {company}!\n\n{cover_letter_content[:400]}...", pdf_path
        
    except Exception as e:
        logger.error(f"Error in generate_cover_letter: {e}")
        return f"Error generating cover letter: {str(e)}", None

def analyze_uploaded_resume(resume_file):
    """Analyze uploaded resume."""
    return toolkit.analyze_resume(resume_file)

def calculate_ats_match(resume_file, job_description):
    """Calculate ATS match score."""
    return toolkit.calculate_ats_score(resume_file, job_description)

def match_user_jobs(skills):
    """Match user skills to jobs."""
    return toolkit.match_jobs(skills)

def calculate_resume_perfection(resume_file):
    """Calculate resume perfection score."""
    return toolkit.calculate_perfection_score(resume_file)

def generate_linkedin_profile(name, job_role, skills, experience):
    """Generate LinkedIn summary."""
    return toolkit.generate_linkedin_summary(name, job_role, skills, experience)

def analyze_skill_gaps(current_skills, target_job):
    """Analyze skill gaps."""
    return toolkit.find_skill_gaps(current_skills, target_job)

def create_dashboard(resume_file, skills, target_job):
    """Create career insights dashboard."""
    return toolkit.create_career_dashboard(resume_file, skills, target_job)