"""
Database Integration Examples for LinkedIn Interest Extractor

Shows how to integrate the extractor with various database systems.
"""

from typing import List, Dict
from linkedin_extractor import LinkedInInterestExtractor


# ============================================================================
# Example 1: SQLite Integration
# ============================================================================

def example_sqlite_integration():
    """Example: Save extracted interests to SQLite database"""
    import sqlite3

    # Initialize database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create tables if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            linkedin_url TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    def save_interests_from_linkedin(telegram_id: int, linkedin_url: str) -> Dict:
        """Process LinkedIn URL and save interests to database"""

        extractor = LinkedInInterestExtractor()

        try:
            # Get or create user
            cursor.execute(
                'INSERT OR IGNORE INTO users (telegram_id, linkedin_url) VALUES (?, ?)',
                (telegram_id, linkedin_url)
            )
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            user_id = cursor.fetchone()[0]

            # Extract interests
            interests = extractor.extract_from_url(linkedin_url, provider="openai")

            # Delete old interests
            cursor.execute('DELETE FROM user_interests WHERE user_id = ?', (user_id,))

            # Save new interests
            for topic in interests:
                cursor.execute(
                    'INSERT INTO user_interests (user_id, topic) VALUES (?, ?)',
                    (user_id, topic)
                )

            conn.commit()

            return {
                'success': True,
                'user_id': user_id,
                'interests': interests,
                'count': len(interests)
            }

        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def get_user_interests(telegram_id: int) -> List[str]:
        """Retrieve user interests from database"""
        cursor.execute('''
            SELECT ui.topic
            FROM user_interests ui
            JOIN users u ON ui.user_id = u.user_id
            WHERE u.telegram_id = ?
        ''', (telegram_id,))

        return [row[0] for row in cursor.fetchall()]

    return save_interests_from_linkedin, get_user_interests


# ============================================================================
# Example 2: PostgreSQL Integration (SQLAlchemy)
# ============================================================================

def example_postgresql_integration():
    """Example: Using SQLAlchemy with PostgreSQL"""
    from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    from datetime import datetime

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'

        user_id = Column(Integer, primary_key=True)
        telegram_id = Column(Integer, unique=True, nullable=False)
        linkedin_url = Column(String(500))
        created_at = Column(DateTime, default=datetime.utcnow)

        interests = relationship('UserInterest', back_populates='user')

    class UserInterest(Base):
        __tablename__ = 'user_interests'

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.user_id'))
        topic = Column(Text, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)

        user = relationship('User', back_populates='interests')

    # Create engine and session
    # engine = create_engine('postgresql://user:pass@localhost/dbname')
    # Session = sessionmaker(bind=engine)

    def save_interests_sqlalchemy(session, telegram_id: int, profile_text: str) -> Dict:
        """Save interests using SQLAlchemy"""
        extractor = LinkedInInterestExtractor()

        try:
            # Get or create user
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(telegram_id=telegram_id)
                session.add(user)
                session.flush()

            # Extract interests
            interests = extractor.extract_from_text(profile_text, provider="openai")

            # Delete old interests
            session.query(UserInterest).filter_by(user_id=user.user_id).delete()

            # Add new interests
            for topic in interests:
                interest = UserInterest(user_id=user.user_id, topic=topic)
                session.add(interest)

            session.commit()

            return {
                'success': True,
                'user_id': user.user_id,
                'interests': interests
            }

        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    return save_interests_sqlalchemy


# ============================================================================
# Example 3: MongoDB Integration
# ============================================================================

def example_mongodb_integration():
    """Example: Using MongoDB/PyMongo"""
    from pymongo import MongoClient
    from datetime import datetime

    # client = MongoClient('mongodb://localhost:27017/')
    # db = client['telegram_bot']

    def save_interests_mongodb(db, telegram_id: int, profile_text: str) -> Dict:
        """Save interests to MongoDB"""
        extractor = LinkedInInterestExtractor()

        try:
            # Extract interests
            interests = extractor.extract_from_text(profile_text, provider="openai")

            # Update or create user document
            result = db.users.update_one(
                {'telegram_id': telegram_id},
                {
                    '$set': {
                        'interests': interests,
                        'updated_at': datetime.utcnow()
                    },
                    '$setOnInsert': {
                        'telegram_id': telegram_id,
                        'created_at': datetime.utcnow()
                    }
                },
                upsert=True
            )

            return {
                'success': True,
                'telegram_id': telegram_id,
                'interests': interests,
                'modified': result.modified_count,
                'upserted': result.upserted_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_interests_mongodb(db, telegram_id: int) -> List[str]:
        """Retrieve user interests from MongoDB"""
        user = db.users.find_one({'telegram_id': telegram_id})
        return user.get('interests', []) if user else []

    return save_interests_mongodb, get_interests_mongodb


# ============================================================================
# Example 4: Telegram Bot Integration
# ============================================================================

def example_telegram_bot_integration():
    """Example: Integrate with python-telegram-bot"""

    # from telegram import Update
    # from telegram.ext import Application, CommandHandler, ContextTypes

    async def handle_add_linkedin(update, context):
        """Handle /add_linkedin command in Telegram bot"""
        from linkedin_extractor import LinkedInInterestExtractor

        # Get LinkedIn URL from command
        if not context.args:
            await update.message.reply_text(
                "Please provide your LinkedIn URL:\n"
                "/add_linkedin https://www.linkedin.com/in/your-username/"
            )
            return

        linkedin_url = context.args[0]
        telegram_id = update.effective_user.id

        # Initialize extractor
        extractor = LinkedInInterestExtractor()

        # Validate URL
        if not extractor.validate_linkedin_url(linkedin_url):
            await update.message.reply_text(
                "❌ Invalid LinkedIn URL. Please provide a valid profile link."
            )
            return

        # Send processing message
        processing_msg = await update.message.reply_text(
            "⏳ Analyzing your LinkedIn profile..."
        )

        try:
            # Extract interests (using text input is recommended)
            # In production, you'd ask user to paste their profile text instead
            await update.message.reply_text(
                "📝 Please paste your LinkedIn 'About' section or profile summary:"
            )

            # Store state to wait for profile text
            context.user_data['waiting_for_profile'] = True
            context.user_data['linkedin_url'] = linkedin_url

        except Exception as e:
            await processing_msg.edit_text(
                f"❌ Error: {str(e)}\n\n"
                "💡 Tip: Try pasting your profile text instead of URL."
            )

    async def handle_profile_text(update, context):
        """Handle profile text input"""
        from linkedin_extractor import LinkedInInterestExtractor

        if not context.user_data.get('waiting_for_profile'):
            return

        profile_text = update.message.text
        telegram_id = update.effective_user.id

        processing_msg = await update.message.reply_text(
            "⏳ Extracting your interests..."
        )

        try:
            extractor = LinkedInInterestExtractor()
            interests = extractor.extract_from_text(profile_text, provider="openai")

            # Save to database (your implementation)
            # save_to_database(telegram_id, interests)

            # Format response
            interests_text = "\n".join([f"  • {topic}" for topic in interests])

            await processing_msg.edit_text(
                f"✅ Great! I found {len(interests)} topics:\n\n"
                f"{interests_text}\n\n"
                f"These interests will help personalize your feed!"
            )

            # Clear state
            context.user_data['waiting_for_profile'] = False

        except Exception as e:
            await processing_msg.edit_text(f"❌ Error: {str(e)}")

    return handle_add_linkedin, handle_profile_text


# ============================================================================
# Example 5: FastAPI REST API Integration
# ============================================================================

def example_fastapi_integration():
    """Example: FastAPI REST API endpoint"""

    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    app = FastAPI()

    class ProfileRequest(BaseModel):
        user_id: str
        profile_text: str
        provider: str = "openai"

    class InterestsResponse(BaseModel):
        success: bool
        user_id: str
        interests: List[str]
        count: int

    @app.post("/extract-interests", response_model=InterestsResponse)
    async def extract_interests(request: ProfileRequest):
        """Extract interests from profile text"""
        from linkedin_extractor import LinkedInInterestExtractor

        extractor = LinkedInInterestExtractor()

        try:
            interests = extractor.extract_from_text(
                request.profile_text,
                provider=request.provider
            )

            # Save to database (your implementation)
            # await save_to_database(request.user_id, interests)

            return InterestsResponse(
                success=True,
                user_id=request.user_id,
                interests=interests,
                count=len(interests)
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/interests/{user_id}")
    async def get_user_interests(user_id: str):
        """Get user's interests"""
        # Fetch from database (your implementation)
        # interests = await fetch_from_database(user_id)

        interests = []  # Placeholder

        return {
            'user_id': user_id,
            'interests': interests
        }

    return app


# ============================================================================
# Example 6: Batch Processing
# ============================================================================

def batch_process_profiles(profiles: List[Dict[str, str]]) -> List[Dict]:
    """
    Process multiple profiles in batch

    Args:
        profiles: List of dicts with 'user_id' and 'profile_text'

    Returns:
        List of results with extracted interests
    """
    from linkedin_extractor import LinkedInInterestExtractor

    extractor = LinkedInInterestExtractor()
    results = []

    for profile in profiles:
        try:
            interests = extractor.extract_from_text(
                profile['profile_text'],
                provider="openai"
            )

            results.append({
                'user_id': profile['user_id'],
                'success': True,
                'interests': interests,
                'count': len(interests)
            })

        except Exception as e:
            results.append({
                'user_id': profile['user_id'],
                'success': False,
                'error': str(e)
            })

    return results


# ============================================================================
# Usage Instructions
# ============================================================================

if __name__ == "__main__":
    print("LinkedIn Interest Extractor - Integration Examples\n")
    print("Available integration examples:")
    print("  1. SQLite - example_sqlite_integration()")
    print("  2. PostgreSQL/SQLAlchemy - example_postgresql_integration()")
    print("  3. MongoDB - example_mongodb_integration()")
    print("  4. Telegram Bot - example_telegram_bot_integration()")
    print("  5. FastAPI REST API - example_fastapi_integration()")
    print("  6. Batch Processing - batch_process_profiles()")
    print("\nChoose the example that matches your tech stack!")
