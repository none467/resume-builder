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
import json
import requests
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import io
import base64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionCareerToolkit:
    def __init__(self):
        """Initialize Production Career Toolkit with API integrations."""
        self.hf_token = os.getenv("HF_TOKEN")
        self.hf_api_url = "https://api-inference.huggingface.co/models/"
        self.mistral_model = "mistralai/Mistral-7B-Instruct-v0.1"
        self.chat_model = "microsoft/DialoGPT-medium"
        
        # Initialize job database and skills
        self.job_database = self.create_comprehensive_job_database()
        self.skills_database = self.create_advanced_skills_database()
        
        # Headers for API requests
        self.headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        
        logger.info("Production Career Toolkit initialized")
    
    def create_comprehensive_job_database(self):
        """Create comprehensive job database with detailed requirements."""
        return {
            'Software Engineer': {
                'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git', 'Docker', 'AWS', 'API Development', 'Testing'],
                'level': 'Mid-Senior',
                'salary_range': '$70,000-$150,000',
                'growth_rate': '22%'
            },
            'Data Scientist': {
                'skills': ['Python', 'R', 'Machine Learning', 'SQL', 'Statistics', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'Data Visualization'],
                'level': 'Mid-Senior',
                'salary_range': '$80,000-$160,000',
                'growth_rate': '31%'
            },
            'Product Manager': {
                'skills': ['Product Strategy', 'Market Research', 'Agile', 'Roadmapping', 'Analytics', 'User Research', 'A/B Testing', 'Communication', 'Leadership'],
                'level': 'Senior',
                'salary_range': '$90,000-$180,000',
                'growth_rate': '19%'
            },
            'Digital Marketing Manager': {
                'skills': ['SEO', 'SEM', 'Google Analytics', 'Social Media Marketing', 'Content Strategy', 'Email Marketing', 'PPC', 'Marketing Automation'],
                'level': 'Mid-Senior',
                'salary_range': '$55,000-$120,000',
                'growth_rate': '10%'
            },
            'UX/UI Designer': {
                'skills': ['Figma', 'Adobe Creative Suite', 'User Research', 'Wireframing', 'Prototyping', 'Design Systems', 'Usability Testing', 'HTML/CSS'],
                'level': 'Mid-Senior',
                'salary_range': '$65,000-$130,000',
                'growth_rate': '13%'
            },
            'DevOps Engineer': {
                'skills': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform', 'Jenkins', 'Monitoring', 'Scripting', 'Cloud Infrastructure'],
                'level': 'Senior',
                'salary_range': '$85,000-$170,000',
                'growth_rate': '25%'
            },
            'Financial Analyst': {
                'skills': ['Excel', 'Financial Modeling', 'SQL', 'Python', 'Tableau', 'Financial Reporting', 'Valuation', 'Risk Analysis', 'Budgeting'],
                'level': 'Entry-Mid',
                'salary_range': '$55,000-$110,000',
                'growth_rate': '6%'
            },
            'Cybersecurity Analyst': {
                'skills': ['Network Security', 'Penetration Testing', 'SIEM', 'Incident Response', 'Risk Assessment', 'Compliance', 'Firewalls', 'Ethical Hacking'],
                'level': 'Mid-Senior',
                'salary_range': '$75,000-$145,000',
                'growth_rate': '33%'
            },
            'Machine Learning Engineer': {
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'MLOps', 'Docker', 'Kubernetes', 'Model Deployment', 'Feature Engineering', 'Deep Learning'],
                'level': 'Senior',
                'salary_range': '$95,000-$200,000',
                'growth_rate': '40%'
            },
            'Content Marketing Specialist': {
                'skills': ['SEO Writing', 'Content Strategy', 'Copywriting', 'WordPress', 'Social Media', 'Research', 'Grammar', 'Content Management', 'Analytics'],
                'level': 'Entry-Mid',
                'salary_range': '$40,000-$80,000',
                'growth_rate': '12%'
            }
        }
    
    def create_advanced_skills_database(self):
        """Create advanced skills database with learning paths."""
        return {
            'Python': {
                'category': 'Programming',
                'difficulty': 'Medium',
                'time_to_learn': '3-6 months',
                'resources': ['Python.org Tutorial', 'Codecademy Python', 'Real Python', 'Automate the Boring Stuff'],
                'certifications': ['PCAP', 'PCPP'],
                'market_demand': 'Very High'
            },
            'JavaScript': {
                'category': 'Programming',
                'difficulty': 'Medium',
                'time_to_learn': '2-4 months',
                'resources': ['MDN Web Docs', 'JavaScript.info', 'FreeCodeCamp', 'Eloquent JavaScript'],
                'certifications': ['AWS Certified Developer'],
                'market_demand': 'Very High'
            },
            'Machine Learning': {
                'category': 'Data Science',
                'difficulty': 'Hard',
                'time_to_learn': '6-12 months',
                'resources': ['Coursera ML Course', 'Fast.ai', 'Kaggle Learn', 'Hands-On ML Book'],
                'certifications': ['Google ML Engineer', 'AWS ML Specialty'],
                'market_demand': 'Very High'
            },
            'React': {
                'category': 'Frontend',
                'difficulty': 'Medium',
                'time_to_learn': '2-3 months',
                'resources': ['React Official Docs', 'React Tutorial', 'Scrimba React Course'],
                'certifications': ['Meta Front-End Developer'],
                'market_demand': 'High'
            },
            'AWS': {
                'category': 'Cloud',
                'difficulty': 'Hard',
                'time_to_learn': '4-8 months',
                'resources': ['AWS Training', 'A Cloud Guru', 'Linux Academy', 'AWS Documentation'],
                'certifications': ['AWS Solutions Architect', 'AWS Developer'],
                'market_demand': 'Very High'
            }
        }
    
    # Real-time AI API Integration
    def query_huggingface_api(self, model_name, payload, max_retries=3):
        """Query Hugging Face Inference API with retry logic."""
        if not self.hf_token:
            return {"error": "Hugging Face token not available"}
        
        url = f"{self.hf_api_url}{model_name}"
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    import time
                    time.sleep(5)
                    continue
                else:
                    logger.error(f"API Error: {response.status_code} - {response.text}")
                    return {"error": f"API Error: {response.status_code}"}
                    
            except requests.exceptions.Timeout:
                logger.error(f"Timeout on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    return {"error": "Request timeout"}
            except Exception as e:
                logger.error(f"API request failed: {e}")
                return {"error": str(e)}
        
        return {"error": "Max retries exceeded"}
    
    def generate_ai_content(self, prompt, max_length=1000):
        """Generate content using Mistral-7B-Instruct model."""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        result = self.query_huggingface_api(self.mistral_model, payload)
        
        if "error" in result:
            return f"AI service temporarily unavailable. Using fallback generation.\n\n{self.create_fallback_content(prompt)}"
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        
        return "Content generation failed. Please try again."
    
    def create_fallback_content(self, prompt):
        """Create intelligent fallback content when AI is unavailable."""
        if "resume" in prompt.lower():
            return "Professional resume content with structured sections including summary, experience, education, and skills."
        elif "cover letter" in prompt.lower():
            return "Professional cover letter with compelling opening, relevant experience highlight, and strong closing."
        else:
            return "Professional content tailored to your requirements."
    
    # Resume Generation with Real-time AI
    def generate_ai_resume(self, name, role, skills, experience, education):
        """Generate resume using real-time AI."""
        if not all([name.strip(), role.strip(), skills.strip(), experience.strip(), education.strip()]):
            return "Please fill in all fields to generate your resume.", None
        
        try:
            prompt = f"""Create a professional resume for:

Name: {name}
Role: {role}
Skills: {skills}
Experience: {experience}
Education: {education}

Generate a well-structured, professional resume with the following sections:
1. Professional Summary (3-4 lines highlighting key strengths)
2. Core Skills (organized and relevant)
3. Professional Experience (with achievements and metrics)
4. Education and Certifications
5. Additional Qualifications

Make it compelling, keyword-rich, and tailored for the {role} position. Use professional language and quantify achievements where possible."""

            ai_content = self.generate_ai_content(prompt, max_length=800)
            
            # Format the content professionally
            formatted_resume = self.format_resume_content(ai_content, name, role)
            
            # Create PDF
            pdf_path = self.create_professional_pdf(formatted_resume, name, "resume")
            
            return f"AI-Generated Resume for {name}\n\n{formatted_resume[:600]}...", pdf_path
            
        except Exception as e:
            logger.error(f"Error generating AI resume: {e}")
            return f"Error generating resume: {str(e)}", None
    
    def format_resume_content(self, content, name, role):
        """Format AI-generated content into professional resume structure."""
        formatted = f"""
{name.upper()}
{role}

{content}

Generated with AI Career Toolkit - {datetime.now().strftime("%B %Y")}
"""
        return formatted.strip()
    
    # Cover Letter Generation with Real-time AI
    def generate_ai_cover_letter(self, name, role, company, skills):
        """Generate cover letter using real-time AI."""
        if not all([name.strip(), role.strip(), company.strip(), skills.strip()]):
            return "Please fill in all fields to generate your cover letter.", None
        
        try:
            prompt = f"""Write a compelling cover letter for:

Name: {name}
Position: {role}
Company: {company}
Key Skills: {skills}

Create a professional cover letter that:
1. Opens with strong interest in the {role} position at {company}
2. Highlights relevant skills: {skills}
3. Shows knowledge of the company
4. Demonstrates value proposition
5. Closes with a call to action

Make it personalized, engaging, and professional. Limit to 3-4 paragraphs."""

            ai_content = self.generate_ai_content(prompt, max_length=600)
            
            # Format the cover letter
            formatted_letter = self.format_cover_letter_content(ai_content, name, role, company)
            
            # Create PDF
            pdf_path = self.create_professional_pdf(formatted_letter, name, "cover_letter")
            
            return f"AI-Generated Cover Letter for {company}\n\n{formatted_letter[:500]}...", pdf_path
            
        except Exception as e:
            logger.error(f"Error generating AI cover letter: {e}")
            return f"Error generating cover letter: {str(e)}", None
    
    def format_cover_letter_content(self, content, name, role, company):
        """Format AI-generated content into professional cover letter structure."""
        formatted = f"""
{name}
{role} Application

{datetime.now().strftime("%B %d, %Y")}

Dear Hiring Manager,

{content}

Sincerely,
{name}
"""
        return formatted.strip()
    
    # Resume Upload & Analysis
    def analyze_resume_advanced(self, resume_file):
        """Advanced resume analysis with AI insights."""
        if resume_file is None:
            return "Please upload a resume file to analyze.", None
        
        try:
            # Extract text from PDF
            resume_text = self.extract_text_from_pdf(resume_file.name)
            
            if not resume_text or len(resume_text.strip()) < 50:
                return "Could not extract sufficient text from the resume. Please ensure the PDF contains readable text.", None
            
            # Perform comprehensive analysis
            analysis = self.perform_comprehensive_analysis(resume_text)
            
            # Generate AI-powered insights
            ai_insights = self.generate_ai_insights(resume_text)
            
            # Create detailed report
            report = self.create_comprehensive_report(analysis, ai_insights)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            return f"Error analyzing resume: {str(e)}", None
    
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
    
    def perform_comprehensive_analysis(self, resume_text):
        """Perform detailed resume analysis."""
        analysis = {
            'sections_found': [],
            'sections_missing': [],
            'word_count': len(resume_text.split()),
            'skills_found': [],
            'contact_info': False,
            'action_verbs': 0,
            'quantified_achievements': 0,
            'keywords_density': {},
            'readability_score': 0
        }
        
        # Check for required sections
        required_sections = ['experience', 'education', 'skills', 'summary', 'objective']
        text_lower = resume_text.lower()
        
        for section in required_sections:
            if section in text_lower or (section == 'summary' and 'profile' in text_lower):
                analysis['sections_found'].append(section.title())
            else:
                analysis['sections_missing'].append(section.title())
        
        # Contact information analysis
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        if re.search(email_pattern, resume_text) or re.search(phone_pattern, resume_text):
            analysis['contact_info'] = True
        
        # Skills analysis
        all_skills = set()
        for job_data in self.job_database.values():
            all_skills.update([skill.lower() for skill in job_data['skills']])
        
        for skill in all_skills:
            if skill.lower() in text_lower:
                analysis['skills_found'].append(skill.title())
        
        # Action verbs analysis
        action_verbs = ['managed', 'developed', 'created', 'implemented', 'designed', 'led', 'improved', 'increased', 'reduced', 'achieved', 'delivered', 'built', 'established', 'coordinated', 'analyzed', 'optimized', 'executed', 'launched', 'collaborated']
        for verb in action_verbs:
            analysis['action_verbs'] += len(re.findall(r'\b' + verb + r'\w*\b', text_lower))
        
        # Quantified achievements
        number_pattern = r'\b\d+(?:\.\d+)?%?\b'
        analysis['quantified_achievements'] = len(re.findall(number_pattern, resume_text))
        
        # Keywords density
        words = resume_text.lower().split()
        word_freq = Counter(words)
        analysis['keywords_density'] = dict(word_freq.most_common(10))
        
        # Simple readability score
        sentences = len(re.split(r'[.!?]+', resume_text))
        if sentences > 0:
            analysis['readability_score'] = min(100, (analysis['word_count'] / sentences) * 2)
        
        return analysis
    
    def generate_ai_insights(self, resume_text):
        """Generate AI-powered insights about the resume."""
        prompt = f"""Analyze this resume and provide professional insights:

{resume_text[:1000]}...

Provide insights on:
1. Overall impression and strengths
2. Areas for improvement
3. Missing elements
4. Suggestions for better formatting
5. Keyword optimization recommendations

Be specific and actionable in your feedback."""

        insights = self.generate_ai_content(prompt, max_length=400)
        return insights
    
    def create_comprehensive_report(self, analysis, ai_insights):
        """Create comprehensive analysis report."""
        score = self.calculate_comprehensive_score(analysis)
        
        report = f"""
COMPREHENSIVE RESUME ANALYSIS
==============================

OVERALL SCORE: {score}/100

SECTIONS ANALYSIS:
✓ Found: {', '.join(analysis['sections_found']) if analysis['sections_found'] else 'None'}
⚠ Missing: {', '.join(analysis['sections_missing']) if analysis['sections_missing'] else 'None'}

CONTENT METRICS:
• Word Count: {analysis['word_count']} words
• Skills Identified: {len(analysis['skills_found'])} 
• Action Verbs Used: {analysis['action_verbs']}
• Quantified Achievements: {analysis['quantified_achievements']}
• Contact Info Present: {'Yes' if analysis['contact_info'] else 'No'}
• Readability Score: {analysis['readability_score']:.1f}/100

TOP KEYWORDS:
{', '.join([f"{word} ({count})" for word, count in list(analysis['keywords_density'].items())[:5]])}

AI-POWERED INSIGHTS:
{ai_insights}

IMPROVEMENT RECOMMENDATIONS:
{self.generate_improvement_recommendations(analysis, score)}
"""
        return report
    
    def calculate_comprehensive_score(self, analysis):
        """Calculate comprehensive resume score."""
        score = 0
        
        # Sections (30 points)
        required_sections = 5
        found_sections = len(analysis['sections_found'])
        score += min(30, (found_sections / required_sections) * 30)
        
        # Content quality (25 points)
        if 300 <= analysis['word_count'] <= 700:
            score += 15
        if analysis['action_verbs'] >= 5:
            score += 5
        if analysis['quantified_achievements'] >= 3:
            score += 5
        
        # Skills (20 points)
        score += min(20, len(analysis['skills_found']) * 2)
        
        # Technical elements (15 points)
        if analysis['contact_info']:
            score += 5
        if analysis['readability_score'] >= 50:
            score += 5
        if analysis['word_count'] >= 200:
            score += 5
        
        # Keywords (10 points)
        if len(analysis['keywords_density']) >= 5:
            score += 10
        
        return int(min(100, score))
    
    def generate_improvement_recommendations(self, analysis, score):
        """Generate specific improvement recommendations."""
        recommendations = []
        
        if len(analysis['sections_missing']) > 0:
            recommendations.append(f"Add missing sections: {', '.join(analysis['sections_missing'])}")
        
        if analysis['word_count'] < 300:
            recommendations.append("Expand content - aim for 300-500 words with more detailed descriptions")
        
        if analysis['action_verbs'] < 5:
            recommendations.append("Use more action verbs to describe achievements")
        
        if analysis['quantified_achievements'] < 3:
            recommendations.append("Add more quantified achievements with specific numbers and percentages")
        
        if len(analysis['skills_found']) < 5:
            recommendations.append("Include more relevant technical and soft skills")
        
        if not analysis['contact_info']:
            recommendations.append("Ensure contact information is clearly visible")
        
        return '\n'.join([f"• {rec}" for rec in recommendations])
    
    # ATS Match Score with Real-time Analysis
    def calculate_ats_score_advanced(self, resume_file, job_description):
        """Calculate advanced ATS match score."""
        if resume_file is None or not job_description.strip():
            return "Please upload a resume file and provide a job description.", None
        
        try:
            resume_text = self.extract_text_from_pdf(resume_file.name)
            
            if not resume_text:
                return "Could not extract text from resume file.", None
            
            # Calculate similarity using multiple methods
            tfidf_score = self.calculate_tfidf_similarity(resume_text, job_description)
            keyword_score = self.calculate_keyword_match(resume_text, job_description)
            
            # Combined ATS score
            ats_score = (tfidf_score * 0.6 + keyword_score * 0.4)
            
            # Generate AI analysis
            ai_analysis = self.generate_ats_ai_analysis(resume_text, job_description, ats_score)
            
            # Create detailed report
            report = self.create_ats_report(ats_score, tfidf_score, keyword_score, ai_analysis)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error calculating ATS score: {e}")
            return f"Error calculating ATS score: {str(e)}", None
    
    def calculate_tfidf_similarity(self, resume_text, job_description):
        """Calculate TF-IDF similarity."""
        documents = [resume_text, job_description]
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix[0, 1] * 100
    
    def calculate_keyword_match(self, resume_text, job_description):
        """Calculate keyword match percentage."""
        # Extract keywords from job description
        job_keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', job_description.lower()))
        resume_keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', resume_text.lower()))
        
        # Filter out common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those', 'will', 'have', 'has', 'had', 'can', 'could', 'should', 'would', 'may', 'might', 'must'}
        job_keywords = job_keywords - common_words
        
        if not job_keywords:
            return 0
        
        matching_keywords = job_keywords & resume_keywords
        return (len(matching_keywords) / len(job_keywords)) * 100
    
    def generate_ats_ai_analysis(self, resume_text, job_description, ats_score):
        """Generate AI analysis of ATS compatibility."""
        prompt = f"""Analyze the ATS compatibility between this resume and job description:

ATS Score: {ats_score:.1f}%

Job Description (first 300 chars): {job_description[:300]}...
Resume (first 300 chars): {resume_text[:300]}...

Provide specific recommendations to improve ATS compatibility:
1. Keywords to add
2. Formatting suggestions
3. Content optimization tips
4. Section improvements"""

        return self.generate_ai_content(prompt, max_length=300)
    
    def create_ats_report(self, ats_score, tfidf_score, keyword_score, ai_analysis):
        """Create comprehensive ATS report."""
        score_level = "Excellent" if ats_score >= 80 else "Good" if ats_score >= 60 else "Fair" if ats_score >= 40 else "Needs Improvement"
        
        report = f"""
ATS COMPATIBILITY ANALYSIS
==========================

OVERALL ATS SCORE: {ats_score:.1f}% ({score_level})

DETAILED BREAKDOWN:
• Content Similarity: {tfidf_score:.1f}%
• Keyword Match: {keyword_score:.1f}%

SCORE INTERPRETATION:
• 80-100%: Excellent - Very likely to pass ATS screening
• 60-79%: Good - Likely to pass with minor optimizations
• 40-59%: Fair - Needs keyword optimization
• Below 40%: Needs significant improvement

AI OPTIMIZATION RECOMMENDATIONS:
{ai_analysis}

NEXT STEPS:
• {"Your resume is well-optimized for ATS systems!" if ats_score >= 80 else "Focus on incorporating missing keywords naturally"}
• {"Maintain current keyword density" if ats_score >= 70 else "Add more job-specific technical terms"}
• {"Consider formatting improvements" if ats_score < 60 else "Current formatting appears ATS-friendly"}
"""
        return report
    
    # Job Matcher with Advanced Algorithm
    def match_jobs_advanced(self, user_skills):
        """Advanced job matching with detailed analysis."""
        if not user_skills.strip():
            return "Please enter your skills to find matching jobs.", None
        
        try:
            user_skills_list = [skill.strip().lower() for skill in user_skills.split(',')]
            job_matches = []
            
            for job_title, job_data in self.job_database.items():
                job_skills = [skill.lower() for skill in job_data['skills']]
                
                # Calculate various match metrics
                exact_matches = set(user_skills_list) & set(job_skills)
                match_percentage = (len(exact_matches) / len(job_skills)) * 100
                
                # Calculate skill coverage
                skill_coverage = (len(exact_matches) / len(user_skills_list)) * 100 if user_skills_list else 0
                
                # Calculate overall compatibility
                compatibility_score = (match_percentage + skill_coverage) / 2
                
                if compatibility_score > 0:
                    missing_skills = set(job_skills) - set(user_skills_list)
                    
                    job_matches.append({
                        'job_title': job_title,
                        'match_percentage': match_percentage,
                        'skill_coverage': skill_coverage,
                        'compatibility_score': compatibility_score,
                        'matching_skills': list(exact_matches),
                        'missing_skills': list(missing_skills),
                        'salary_range': job_data['salary_range'],
                        'growth_rate': job_data['growth_rate'],
                        'level': job_data['level']
                    })
            
            # Sort by compatibility score
            job_matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
            
            # Generate AI insights for top matches
            ai_insights = self.generate_job_match_insights(job_matches[:3], user_skills_list)
            
            # Create comprehensive report
            report = self.create_job_match_report(job_matches[:5], user_skills_list, ai_insights)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error matching jobs: {e}")
            return f"Error matching jobs: {str(e)}", None
    
    def generate_job_match_insights(self, top_matches, user_skills):
        """Generate AI insights for job matches."""
        if not top_matches:
            return "No strong matches found."
        
        top_job = top_matches[0]
        prompt = f"""Provide career advice for someone with skills: {', '.join(user_skills)}

Top matching job: {top_job['job_title']} ({top_job['compatibility_score']:.1f}% match)
Salary range: {top_job['salary_range']}
Growth rate: {top_job['growth_rate']}

Provide advice on:
1. Career progression opportunities
2. Skills to prioritize for development
3. Market trends for this role
4. Salary negotiation tips"""

        return self.generate_ai_content(prompt, max_length=300)
    
    def create_job_match_report(self, job_matches, user_skills, ai_insights):
        """Create comprehensive job matching report."""
        if not job_matches:
            return "No matching jobs found. Consider expanding your skillset or exploring related fields."
        
        report = f"""
ADVANCED JOB MATCHING ANALYSIS
==============================

YOUR SKILLS: {', '.join(user_skills)}

TOP 5 MATCHING POSITIONS:

"""
        
        for i, match in enumerate(job_matches, 1):
            report += f"""
{i}. {match['job_title']} - {match['compatibility_score']:.1f}% Compatibility
   💰 Salary: {match['salary_range']}
   📈 Growth Rate: {match['growth_rate']}
   📊 Level: {match['level']}
   ✓ Skills Match: {match['match_percentage']:.1f}%
   📋 Your Coverage: {match['skill_coverage']:.1f}%
   🎯 Matching Skills: {', '.join(match['matching_skills'][:4])}{'...' if len(match['matching_skills']) > 4 else ''}
   📚 Skills to Learn: {', '.join(match['missing_skills'][:3])}{'...' if len(match['missing_skills']) > 3 else ''}

"""
        
        report += f"""
AI CAREER INSIGHTS:
{ai_insights}

MARKET ANALYSIS:
• Best Match: {job_matches[0]['job_title']} with {job_matches[0]['compatibility_score']:.1f}% compatibility
• Average Salary Range: {self.calculate_average_salary(job_matches[:3])}
• Highest Growth Rate: {max([match['growth_rate'] for match in job_matches[:3]])}
"""
        
        return report
    
    def calculate_average_salary(self, matches):
        """Calculate average salary range from matches."""
        if not matches:
            return "N/A"
        
        # Simple average calculation for display
        return f"${sum([int(match['salary_range'].split('-')[0].replace('$', '').replace(',', '')) for match in matches]) // len(matches):,}+"
    
    # Resume Perfection Score with Real-time AI
    def calculate_perfection_score_ai(self, resume_file):
        """Calculate AI-powered resume perfection score."""
        if resume_file is None:
            return "Please upload a resume file to calculate the perfection score.", None
        
        try:
            resume_text = self.extract_text_from_pdf(resume_file.name)
            if not resume_text:
                return "Could not extract text from resume file.", None
            
            # Perform analysis
            analysis = self.perform_comprehensive_analysis(resume_text)
            
            # Get AI evaluation
            ai_evaluation = self.generate_ai_evaluation(resume_text)
            
            # Calculate detailed scores
            scores = self.calculate_detailed_perfection_scores(analysis, resume_text)
            
            # Create comprehensive report
            report = self.create_perfection_report(scores, ai_evaluation)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error calculating perfection score: {e}")
            return f"Error calculating perfection score: {str(e)}", None
    
    def generate_ai_evaluation(self, resume_text):
        """Generate AI evaluation of resume quality."""
        prompt = f"""Evaluate this resume comprehensively:

{resume_text[:800]}...

Rate the resume (1-100) on:
1. Professional presentation
2. Content quality and relevance
3. Achievement quantification
4. Keyword optimization
5. Overall impact

Provide specific improvement recommendations and highlight strengths."""

        return self.generate_ai_content(prompt, max_length=400)
    
    def calculate_detailed_perfection_scores(self, analysis, resume_text):
        """Calculate detailed perfection scores."""
        scores = {
            'structure': min(25, len(analysis['sections_found']) * 5),
            'content': min(25, (analysis['action_verbs'] * 2) + (analysis['quantified_achievements'] * 3)),
            'keywords': min(20, len(analysis['skills_found']) * 2),
            'formatting': min(15, 15 if 300 <= analysis['word_count'] <= 700 else 10),
            'professionalism': min(15, 15 if analysis['contact_info'] else 10),
            'overall': 0
        }
        
        scores['overall'] = sum(scores.values()) - scores['overall']
        return scores
    
    def create_perfection_report(self, scores, ai_evaluation):
        """Create perfection score report."""
        overall_score = scores['overall']
        grade = "A+" if overall_score >= 90 else "A" if overall_score >= 80 else "B+" if overall_score >= 70 else "B" if overall_score >= 60 else "C"
        
        report = f"""
AI-POWERED RESUME PERFECTION ANALYSIS
=====================================

OVERALL SCORE: {overall_score}/100 (Grade: {grade})

DETAILED BREAKDOWN:
📋 Structure & Sections: {scores['structure']}/25
📝 Content Quality: {scores['content']}/25
🔍 Keywords & Skills: {scores['keywords']}/20
🎨 Formatting: {scores['formatting']}/15
💼 Professionalism: {scores['professionalism']}/15

AI EXPERT EVALUATION:
{ai_evaluation}

PERFORMANCE LEVEL:
{self.get_performance_level(overall_score)}

OPTIMIZATION PRIORITY:
{self.get_optimization_priority(scores)}
"""
        return report
    
    def get_performance_level(self, score):
        """Get performance level description."""
        if score >= 90:
            return "🏆 EXCEPTIONAL - Top 5% of resumes"
        elif score >= 80:
            return "🌟 EXCELLENT - Strong competitive advantage"
        elif score >= 70:
            return "✅ GOOD - Solid foundation with room for improvement"
        elif score >= 60:
            return "⚠️ FAIR - Needs optimization for better results"
        else:
            return "🔧 NEEDS WORK - Significant improvements required"
    
    def get_optimization_priority(self, scores):
        """Get optimization priority recommendations."""
        lowest_score = min(scores.items(), key=lambda x: x[1] if x[0] != 'overall' else 100)
        
        priorities = {
            'structure': "Focus on adding missing resume sections",
            'content': "Improve content with more action verbs and quantified achievements",
            'keywords': "Add more relevant industry keywords and technical skills",
            'formatting': "Optimize formatting and length for better readability",
            'professionalism': "Ensure professional presentation and contact information"
        }
        
        return priorities.get(lowest_score[0], "Continue optimizing all areas")
    
    # LinkedIn Summary Generator
    def generate_linkedin_summary_ai(self, name, role, skills, experience):
        """Generate AI-powered LinkedIn summary."""
        if not all([name.strip(), role.strip(), skills.strip()]):
            return "Please fill in name, role, and skills to generate LinkedIn summary.", None
        
        try:
            prompt = f"""Create a compelling LinkedIn summary for:

Name: {name}
Role: {role}
Skills: {skills}
Experience: {experience}

Write a professional, engaging LinkedIn summary that:
1. Starts with a strong hook
2. Highlights key achievements and skills
3. Shows personality and passion
4. Includes a call-to-action
5. Uses relevant keywords for the {role} field

Keep it conversational yet professional, around 150-200 words."""

            ai_summary = self.generate_ai_content(prompt, max_length=400)
            
            # Format for LinkedIn
            formatted_summary = self.format_linkedin_summary(ai_summary, name, role, skills)
            
            return formatted_summary, None
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn summary: {e}")
            return f"Error generating LinkedIn summary: {str(e)}", None
    
    def format_linkedin_summary(self, ai_content, name, role, skills):
        """Format AI-generated content for LinkedIn."""
        skills_hashtags = ' '.join([f"#{skill.replace(' ', '')}" for skill in skills.split(',')[:5]])
        
        formatted = f"""
{ai_content}

{skills_hashtags}
#OpenToWork #CareerOpportunities #{role.replace(' ', '')}

---
Generated with AI Career Toolkit
"""
        return formatted.strip()
    
    # Skill Gap Finder with Learning Resources
    def find_skill_gaps_advanced(self, current_skills, target_job):
        """Advanced skill gap analysis with learning resources."""
        if not current_skills.strip() or not target_job.strip():
            return "Please enter your current skills and target job role.", None
        
        try:
            current_skills_list = [skill.strip().lower() for skill in current_skills.split(',')]
            
            # Find target job requirements
            target_job_data = None
            for job_title, job_data in self.job_database.items():
                if target_job.lower() in job_title.lower():
                    target_job_data = job_data
                    break
            
            if not target_job_data:
                # Find partial matches
                for job_title, job_data in self.job_database.items():
                    if any(word in job_title.lower() for word in target_job.lower().split()):
                        target_job_data = job_data
                        break
            
            if not target_job_data:
                return f"Job role '{target_job}' not found. Available roles: {', '.join(list(self.job_database.keys())[:5])}", None
            
            # Calculate gaps
            target_skills = [skill.lower() for skill in target_job_data['skills']]
            matching_skills = set(current_skills_list) & set(target_skills)
            missing_skills = set(target_skills) - set(current_skills_list)
            
            # Generate AI learning recommendations
            ai_recommendations = self.generate_learning_recommendations(missing_skills, target_job)
            
            # Create comprehensive report
            report = self.create_skill_gap_report(target_job, matching_skills, missing_skills, target_job_data, ai_recommendations)
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error finding skill gaps: {e}")
            return f"Error finding skill gaps: {str(e)}", None
    
    def generate_learning_recommendations(self, missing_skills, target_job):
        """Generate AI-powered learning recommendations."""
        if not missing_skills:
            return "You have all the required skills!"
        
        skills_list = ', '.join(missing_skills)
        prompt = f"""Create a learning roadmap for someone targeting a {target_job} role who needs to develop these skills: {skills_list}

Provide:
1. Learning priority order
2. Estimated time to learn each skill
3. Best learning resources and platforms
4. Project ideas to practice each skill
5. Certification recommendations

Make it practical and actionable."""

        return self.generate_ai_content(prompt, max_length=500)
    
    def create_skill_gap_report(self, target_job, matching_skills, missing_skills, job_data, ai_recommendations):
        """Create comprehensive skill gap report."""
        match_percentage = (len(matching_skills) / len(job_data['skills'])) * 100
        
        report = f"""
ADVANCED SKILL GAP ANALYSIS
===========================

TARGET ROLE: {target_job.title()}
ROLE LEVEL: {job_data['level']}
SALARY RANGE: {job_data['salary_range']}
GROWTH RATE: {job_data['growth_rate']}

SKILL COMPATIBILITY: {match_percentage:.1f}%

✅ SKILLS YOU HAVE ({len(matching_skills)}):
{', '.join([skill.title() for skill in matching_skills]) if matching_skills else 'None identified'}

📚 SKILLS TO DEVELOP ({len(missing_skills)}):
{', '.join([skill.title() for skill in missing_skills]) if missing_skills else 'None - you have all required skills!'}

AI LEARNING ROADMAP:
{ai_recommendations}

MARKET INSIGHTS:
• Job Growth Rate: {job_data['growth_rate']} (above average indicates high demand)
• Salary Potential: {job_data['salary_range']}
• Experience Level: {job_data['level']} positions available

READINESS ASSESSMENT:
{self.assess_job_readiness(match_percentage, len(matching_skills))}
"""
        
        return report
    
    def assess_job_readiness(self, match_percentage, skills_count):
        """Assess job readiness based on skill match."""
        if match_percentage >= 80:
            return "🚀 READY TO APPLY - You meet most requirements"
        elif match_percentage >= 60:
            return "💪 ALMOST READY - Focus on 1-2 key skills (3-6 months)"
        elif match_percentage >= 40:
            return "📈 DEVELOPING - Significant skill development needed (6-12 months)"
        else:
            return "📚 EARLY STAGE - Consider foundational learning (12+ months)"
    
    # Career Insights Dashboard with Plotly
    def create_career_dashboard_advanced(self, resume_file, skills, target_job):
        """Create advanced career insights dashboard."""
        if not skills.strip():
            return "Please enter your skills to generate career insights.", None, None
        
        try:
            insights = self.gather_comprehensive_insights(resume_file, skills, target_job)
            
            # Generate visualizations
            dashboard_plots = self.create_advanced_visualizations(insights)
            
            # Create executive summary
            summary = self.create_executive_summary(insights, target_job)
            
            return summary, dashboard_plots, None
            
        except Exception as e:
            logger.error(f"Error creating career dashboard: {e}")
            return f"Error creating career dashboard: {str(e)}", None, None
    
    def gather_comprehensive_insights(self, resume_file, skills, target_job):
        """Gather comprehensive career insights."""
        insights = {
            'skills': skills.split(','),
            'skill_count': len(skills.split(',')),
            'resume_score': 0,
            'ats_score': 0,
            'job_match': 0,
            'market_demand': 'Medium',
            'salary_potential': 'N/A',
            'readiness_level': 'Developing'
        }
        
        # Analyze resume if provided
        if resume_file:
            try:
                resume_text = self.extract_text_from_pdf(resume_file.name)
                if resume_text:
                    analysis = self.perform_comprehensive_analysis(resume_text)
                    insights['resume_score'] = self.calculate_comprehensive_score(analysis)
            except:
                pass
        
        # Analyze job match if target job provided
        if target_job and target_job in self.job_database:
            job_data = self.job_database[target_job]
            user_skills = [s.strip().lower() for s in skills.split(',')]
            job_skills = [s.lower() for s in job_data['skills']]
            
            matching = set(user_skills) & set(job_skills)
            insights['job_match'] = (len(matching) / len(job_skills)) * 100
            insights['salary_potential'] = job_data['salary_range']
            insights['market_demand'] = 'High' if float(job_data['growth_rate'].rstrip('%')) > 15 else 'Medium'
        
        # Calculate overall readiness
        overall_score = (insights['resume_score'] + insights['job_match']) / 2
        if overall_score >= 80:
            insights['readiness_level'] = "Ready to Apply"
        elif overall_score >= 60:
            insights['readiness_level'] = "Almost Ready"
        elif overall_score >= 40:
            insights['readiness_level'] = "Developing"
        else:
            insights['readiness_level'] = "Early Stage"
        
        return insights
    
    def create_advanced_visualizations(self, insights):
        """Create advanced Plotly visualizations."""
        try:
            # Create subplot figure
            fig = go.Figure()
            
            # Career Readiness Gauge
            fig.add_trace(go.Indicator(
                mode = "gauge+number+delta",
                value = (insights['resume_score'] + insights['job_match']) / 2,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Career Readiness Score"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(
                title="Career Readiness Dashboard",
                height=400,
                font={'size': 12}
            )
            
            # Save plot
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", prefix="career_dashboard_")
            fig.write_html(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return None
    
    def create_executive_summary(self, insights, target_job):
        """Create executive career summary."""
        readiness_score = (insights['resume_score'] + insights['job_match']) / 2
        
        summary = f"""
EXECUTIVE CAREER INSIGHTS DASHBOARD
===================================

🎯 TARGET ROLE: {target_job.title() if target_job else 'Multiple Roles'}

📊 KEY PERFORMANCE INDICATORS:
• Overall Readiness Score: {readiness_score:.1f}/100
• Resume Quality: {insights['resume_score']}/100
• Job Match Compatibility: {insights['job_match']:.1f}%
• Skills Portfolio: {insights['skill_count']} skills
• Market Demand: {insights['market_demand']}
• Salary Potential: {insights['salary_potential']}

🚀 READINESS LEVEL: {insights['readiness_level']}

💡 STRATEGIC RECOMMENDATIONS:

Resume Optimization:
• {"Maintain excellent resume quality" if insights['resume_score'] >= 80 else "Focus on resume improvements for better ATS compatibility"}

Skill Development:
• {"Strong skill portfolio - focus on specialization" if insights['skill_count'] >= 8 else "Expand skillset with in-demand technologies"}

Market Positioning:
• {"Ready for senior-level applications" if readiness_score >= 75 else "Target entry to mid-level positions"}

🎯 90-DAY ACTION PLAN:
1. {self.get_action_item(insights, 'immediate')}
2. {self.get_action_item(insights, 'short_term')}
3. {self.get_action_item(insights, 'medium_term')}

📈 CAREER TRAJECTORY: {self.predict_career_trajectory(readiness_score, insights)}
"""
        return summary
    
    def get_action_item(self, insights, timeframe):
        """Get specific action items based on timeframe."""
        if timeframe == 'immediate':
            if insights['resume_score'] < 70:
                return "Optimize resume with quantified achievements and keywords"
            return "Apply to 5-10 relevant positions"
        elif timeframe == 'short_term':
            if insights['job_match'] < 60:
                return "Develop 2-3 high-priority skills for target role"
            return "Network with industry professionals and attend virtual events"
        else:
            return "Consider advanced certifications or specialization training"
    
    def predict_career_trajectory(self, readiness_score, insights):
        """Predict career trajectory."""
        if readiness_score >= 85:
            return "Senior/Lead positions within 6-12 months"
        elif readiness_score >= 70:
            return "Mid-level advancement within 12-18 months"
        else:
            return "Skill development phase: 6-18 months before major advancement"
    
    # AI Career Chatbot
    def create_career_chatbot_response(self, message, history):
        """Create AI-powered career chatbot response."""
        try:
            # Context-aware prompt based on conversation history
            context = self.build_chat_context(history)
            
            prompt = f"""You are an expert career advisor AI. Help users with career questions, resume advice, job search strategies, and professional development.

Previous conversation context:
{context}

Current question: {message}

Provide helpful, specific, and actionable career advice. Be encouraging and professional."""

            response = self.generate_ai_content(prompt, max_length=300)
            
            if not response or "error" in response.lower():
                response = self.get_fallback_career_response(message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return "I'm here to help with your career questions! Could you please rephrase your question?"
    
    def build_chat_context(self, history):
        """Build context from chat history."""
        if not history:
            return "No previous context."
        
        # Get last 3 exchanges for context
        recent_history = history[-3:] if len(history) > 3 else history
        context_parts = []
        
        for user_msg, bot_msg in recent_history:
            context_parts.append(f"User: {user_msg}")
            context_parts.append(f"Assistant: {bot_msg}")
        
        return "\n".join(context_parts)
    
    def get_fallback_career_response(self, message):
        """Get fallback response for career questions."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['resume', 'cv']):
            return "For resume advice, I recommend focusing on quantified achievements, relevant keywords, and clear formatting. Would you like specific tips for your industry?"
        
        elif any(word in message_lower for word in ['interview', 'job search']):
            return "Job search success comes from tailored applications, networking, and interview preparation. What specific aspect would you like guidance on?"
        
        elif any(word in message_lower for word in ['skills', 'learning']):
            return "Skill development should align with your career goals. Consider both technical skills and soft skills. What role are you targeting?"
        
        else:
            return "I'm here to help with career advice! Feel free to ask about resumes, job searching, interviews, skill development, or career planning."
    
    # PDF Creation with Professional Formatting
    def create_professional_pdf(self, content, name, doc_type):
        """Create professionally formatted PDF."""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            
            # Professional margins
            pdf.set_left_margin(20)
            pdf.set_right_margin(20)
            pdf.set_top_margin(20)
            
            # Add header
            pdf.set_font("Arial", 'B', 16)
            if doc_type == "resume":
                pdf.cell(0, 15, "PROFESSIONAL RESUME", ln=True, align='C')
            else:
                pdf.cell(0, 15, "COVER LETTER", ln=True, align='C')
            
            pdf.ln(5)
            pdf.set_font("Arial", size=11)
            
            # Process content
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(3)
                    continue
                
                # Format headers
                if line.isupper() and len(line) > 3:
                    pdf.set_font("Arial", 'B', 12)
                    pdf.ln(3)
                    pdf.cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    pdf.ln(2)
                    pdf.set_font("Arial", size=11)
                else:
                    # Handle text wrapping
                    if len(line) > 90:
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 90:
                                current_line += word + " "
                            else:
                                pdf.cell(0, 6, current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                                current_line = word + " "
                        if current_line:
                            pdf.cell(0, 6, current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    else:
                        pdf.cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
            
            # Add footer
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 5, f"Generated by AI Career Toolkit - {datetime.now().strftime('%B %Y')}", ln=True, align='C')
            
            # Save PDF
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", 
                                                   prefix=f"{name.replace(' ', '_')}_{doc_type}_")
            pdf.output(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating professional PDF: {e}")
            raise Exception(f"Failed to create PDF: {e}")

# Initialize the production toolkit
production_toolkit = ProductionCareerToolkit()

# Main interface functions
def generate_ai_resume_interface(name, role, skills, experience, education):
    """Interface function for AI resume generation."""
    return production_toolkit.generate_ai_resume(name, role, skills, experience, education)

def generate_ai_cover_letter_interface(name, role, company, skills):
    """Interface function for AI cover letter generation."""
    return production_toolkit.generate_ai_cover_letter(name, role, company, skills)

def analyze_resume_interface(resume_file):
    """Interface function for resume analysis."""
    return production_toolkit.analyze_resume_advanced(resume_file)

def calculate_ats_interface(resume_file, job_description):
    """Interface function for ATS calculation."""
    return production_toolkit.calculate_ats_score_advanced(resume_file, job_description)

def match_jobs_interface(skills):
    """Interface function for job matching."""
    return production_toolkit.match_jobs_advanced(skills)

def calculate_perfection_interface(resume_file):
    """Interface function for perfection score."""
    return production_toolkit.calculate_perfection_score_ai(resume_file)

def generate_linkedin_interface(name, role, skills, experience):
    """Interface function for LinkedIn generation."""
    return production_toolkit.generate_linkedin_summary_ai(name, role, skills, experience)

def analyze_skill_gaps_interface(current_skills, target_job):
    """Interface function for skill gap analysis."""
    return production_toolkit.find_skill_gaps_advanced(current_skills, target_job)

def create_dashboard_interface(resume_file, skills, target_job):
    """Interface function for career dashboard."""
    return production_toolkit.create_career_dashboard_advanced(resume_file, skills, target_job)

def chatbot_interface(message, history):
    """Interface function for career chatbot."""
    return production_toolkit.create_career_chatbot_response(message, history)