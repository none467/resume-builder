import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timezone
import logging
import hashlib

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        """Initialize database connection and create tables."""
        self.database_url = os.getenv("DATABASE_URL")
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def create_tables(self):
        """Create necessary database tables."""
        tables = {
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    profile_data JSONB DEFAULT '{}'::jsonb
                )
            ''',
            'resumes': '''
                CREATE TABLE IF NOT EXISTS resumes (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    resume_name VARCHAR(255) NOT NULL,
                    content TEXT,
                    job_role VARCHAR(255),
                    skills TEXT[],
                    experience TEXT,
                    education TEXT,
                    pdf_path VARCHAR(500),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    analysis_score INTEGER DEFAULT 0,
                    ats_scores JSONB DEFAULT '{}'::jsonb
                )
            ''',
            'cover_letters': '''
                CREATE TABLE IF NOT EXISTS cover_letters (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    company_name VARCHAR(255) NOT NULL,
                    job_role VARCHAR(255) NOT NULL,
                    content TEXT,
                    pdf_path VARCHAR(500),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'job_applications': '''
                CREATE TABLE IF NOT EXISTS job_applications (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    company_name VARCHAR(255) NOT NULL,
                    job_title VARCHAR(255) NOT NULL,
                    job_description TEXT,
                    resume_id INTEGER REFERENCES resumes(id),
                    cover_letter_id INTEGER REFERENCES cover_letters(id),
                    application_status VARCHAR(50) DEFAULT 'draft',
                    ats_score FLOAT DEFAULT 0,
                    applied_date TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''',
            'skill_assessments': '''
                CREATE TABLE IF NOT EXISTS skill_assessments (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    target_role VARCHAR(255),
                    current_skills TEXT[],
                    missing_skills TEXT[],
                    skill_gap_score FLOAT,
                    learning_recommendations JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'chat_history': '''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    session_id VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    feedback_rating INTEGER DEFAULT NULL,
                    message_category VARCHAR(100)
                )
            ''',
            'analytics': '''
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    action_type VARCHAR(100) NOT NULL,
                    action_data JSONB DEFAULT '{}'::jsonb,
                    session_id VARCHAR(255),
                    ip_address INET,
                    user_agent TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }
        
        try:
            with self.connection.cursor() as cursor:
                for table_name, table_sql in tables.items():
                    cursor.execute(table_sql)
                    logger.info(f"Table {table_name} created/verified")
                
                # Create indexes for better performance
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_cover_letters_user_id ON cover_letters(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_job_applications_user_id ON job_applications(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_analytics_action_type ON analytics(action_type);",
                    "CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at);"
                ]
                
                for index_sql in indexes:
                    cursor.execute(index_sql)
                
                self.connection.commit()
                logger.info("Database tables and indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.connection.rollback()
            raise
    
    def generate_user_id(self, name=None, email=None):
        """Generate a unique user ID based on session or provided info."""
        if email:
            return hashlib.md5(email.lower().encode()).hexdigest()[:16]
        elif name:
            return hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        else:
            return hashlib.md5(f"anonymous_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    
    def create_or_get_user(self, name=None, email=None, user_id=None):
        """Create or retrieve a user."""
        try:
            if not user_id:
                user_id = self.generate_user_id(name, email)
            
            with self.connection.cursor() as cursor:
                # Check if user exists
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                
                if user:
                    # Update last active
                    cursor.execute(
                        "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = %s",
                        (user_id,)
                    )
                    self.connection.commit()
                    return dict(user)
                else:
                    # Create new user
                    cursor.execute(
                        """INSERT INTO users (user_id, name, email, profile_data) 
                           VALUES (%s, %s, %s, %s) RETURNING *""",
                        (user_id, name, email, json.dumps({}))
                    )
                    user = cursor.fetchone()
                    self.connection.commit()
                    logger.info(f"New user created: {user_id}")
                    return dict(user)
                    
        except Exception as e:
            logger.error(f"Error creating/getting user: {e}")
            self.connection.rollback()
            return None
    
    def save_resume(self, user_id, resume_data):
        """Save a generated resume to the database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO resumes 
                       (user_id, resume_name, content, job_role, skills, experience, education, pdf_path, analysis_score)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (
                        user_id,
                        resume_data.get('name', 'Untitled Resume'),
                        resume_data.get('content'),
                        resume_data.get('job_role'),
                        resume_data.get('skills', []),
                        resume_data.get('experience'),
                        resume_data.get('education'),
                        resume_data.get('pdf_path'),
                        resume_data.get('analysis_score', 0)
                    )
                )
                resume_id = cursor.fetchone()['id']
                self.connection.commit()
                logger.info(f"Resume saved for user {user_id}: {resume_id}")
                return resume_id
                
        except Exception as e:
            logger.error(f"Error saving resume: {e}")
            self.connection.rollback()
            return None
    
    def save_cover_letter(self, user_id, cover_letter_data):
        """Save a generated cover letter to the database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO cover_letters 
                       (user_id, company_name, job_role, content, pdf_path)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                    (
                        user_id,
                        cover_letter_data.get('company_name'),
                        cover_letter_data.get('job_role'),
                        cover_letter_data.get('content'),
                        cover_letter_data.get('pdf_path')
                    )
                )
                cover_letter_id = cursor.fetchone()['id']
                self.connection.commit()
                logger.info(f"Cover letter saved for user {user_id}: {cover_letter_id}")
                return cover_letter_id
                
        except Exception as e:
            logger.error(f"Error saving cover letter: {e}")
            self.connection.rollback()
            return None
    
    def save_job_application(self, user_id, application_data):
        """Save job application tracking information."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO job_applications 
                       (user_id, company_name, job_title, job_description, resume_id, cover_letter_id, 
                        application_status, ats_score, applied_date, notes)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (
                        user_id,
                        application_data.get('company_name'),
                        application_data.get('job_title'),
                        application_data.get('job_description'),
                        application_data.get('resume_id'),
                        application_data.get('cover_letter_id'),
                        application_data.get('status', 'draft'),
                        application_data.get('ats_score', 0),
                        application_data.get('applied_date'),
                        application_data.get('notes')
                    )
                )
                application_id = cursor.fetchone()['id']
                self.connection.commit()
                logger.info(f"Job application saved for user {user_id}: {application_id}")
                return application_id
                
        except Exception as e:
            logger.error(f"Error saving job application: {e}")
            self.connection.rollback()
            return None
    
    def save_skill_assessment(self, user_id, assessment_data):
        """Save skill gap assessment results."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO skill_assessments 
                       (user_id, target_role, current_skills, missing_skills, skill_gap_score, learning_recommendations)
                       VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                    (
                        user_id,
                        assessment_data.get('target_role'),
                        assessment_data.get('current_skills', []),
                        assessment_data.get('missing_skills', []),
                        assessment_data.get('skill_gap_score', 0),
                        json.dumps(assessment_data.get('learning_recommendations', {}))
                    )
                )
                assessment_id = cursor.fetchone()['id']
                self.connection.commit()
                logger.info(f"Skill assessment saved for user {user_id}: {assessment_id}")
                return assessment_id
                
        except Exception as e:
            logger.error(f"Error saving skill assessment: {e}")
            self.connection.rollback()
            return None
    
    def save_chat_message(self, user_id, user_message, ai_response, session_id=None, category=None):
        """Save chat conversation to database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO chat_history 
                       (user_id, user_message, ai_response, session_id, message_category)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                    (user_id, user_message, ai_response, session_id, category)
                )
                chat_id = cursor.fetchone()['id']
                self.connection.commit()
                return chat_id
                
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            self.connection.rollback()
            return None
    
    def log_analytics(self, user_id, action_type, action_data=None, session_id=None):
        """Log user analytics and actions."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO analytics 
                       (user_id, action_type, action_data, session_id)
                       VALUES (%s, %s, %s, %s)""",
                    (user_id, action_type, json.dumps(action_data or {}), session_id)
                )
                self.connection.commit()
                
        except Exception as e:
            logger.error(f"Error logging analytics: {e}")
            self.connection.rollback()
    
    def get_user_resumes(self, user_id, limit=10):
        """Get user's recent resumes."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM resumes 
                       WHERE user_id = %s 
                       ORDER BY created_at DESC 
                       LIMIT %s""",
                    (user_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching user resumes: {e}")
            return []
    
    def get_user_cover_letters(self, user_id, limit=10):
        """Get user's recent cover letters."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM cover_letters 
                       WHERE user_id = %s 
                       ORDER BY created_at DESC 
                       LIMIT %s""",
                    (user_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching user cover letters: {e}")
            return []
    
    def get_user_job_applications(self, user_id):
        """Get user's job applications with related data."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT ja.*, r.resume_name, cl.company_name as cl_company
                       FROM job_applications ja
                       LEFT JOIN resumes r ON ja.resume_id = r.id
                       LEFT JOIN cover_letters cl ON ja.cover_letter_id = cl.id
                       WHERE ja.user_id = %s 
                       ORDER BY ja.created_at DESC""",
                    (user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching job applications: {e}")
            return []
    
    def get_user_analytics(self, user_id, days=30):
        """Get user analytics for the specified period."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT action_type, COUNT(*) as count, 
                       DATE_TRUNC('day', created_at) as date
                       FROM analytics 
                       WHERE user_id = %s 
                       AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
                       GROUP BY action_type, DATE_TRUNC('day', created_at)
                       ORDER BY date DESC""",
                    (user_id, days)
                )
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching user analytics: {e}")
            return []
    
    def get_user_dashboard_data(self, user_id):
        """Get comprehensive dashboard data for a user."""
        try:
            dashboard_data = {
                'user': self.create_or_get_user(user_id=user_id),
                'resumes': self.get_user_resumes(user_id, limit=5),
                'cover_letters': self.get_user_cover_letters(user_id, limit=5),
                'job_applications': self.get_user_job_applications(user_id),
                'analytics': self.get_user_analytics(user_id)
            }
            
            # Calculate summary statistics
            with self.connection.cursor() as cursor:
                # Total documents created
                cursor.execute(
                    """SELECT 
                       (SELECT COUNT(*) FROM resumes WHERE user_id = %s) as total_resumes,
                       (SELECT COUNT(*) FROM cover_letters WHERE user_id = %s) as total_cover_letters,
                       (SELECT COUNT(*) FROM job_applications WHERE user_id = %s) as total_applications,
                       (SELECT AVG(analysis_score) FROM resumes WHERE user_id = %s AND analysis_score > 0) as avg_resume_score""",
                    (user_id, user_id, user_id, user_id)
                )
                stats = dict(cursor.fetchone())
                dashboard_data['stats'] = stats
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return None
    
    def search_resumes(self, user_id, search_term):
        """Search user's resumes by content or job role."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM resumes 
                       WHERE user_id = %s 
                       AND (content ILIKE %s OR job_role ILIKE %s OR resume_name ILIKE %s)
                       ORDER BY created_at DESC""",
                    (user_id, f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
                )
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error searching resumes: {e}")
            return []
    
    def update_resume_analysis(self, resume_id, analysis_score, ats_scores=None):
        """Update resume analysis scores."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE resumes 
                       SET analysis_score = %s, ats_scores = %s, updated_at = CURRENT_TIMESTAMP
                       WHERE id = %s""",
                    (analysis_score, json.dumps(ats_scores or {}), resume_id)
                )
                self.connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating resume analysis: {e}")
            self.connection.rollback()
            return False
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# Global database instance
db_manager = None

def get_db_manager():
    """Get global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager