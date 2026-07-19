"""Phase 8, Step 8.2: Generate User Preferences"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid, random
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserPreference, User

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_user_preferences():
    session = Session()
    users = session.query(User).all()
    prefs = []
    for user in users:
        if random.choice([True, False]):
            prefs.append(UserPreference(id=uuid.uuid4(), user_id=user.id, preference_key="ui_format", preference_value=random.choice(["table","chart"]), created_by="generate_user_preferences.py", is_active=True))
        if len(prefs) < 25:
            prefs.append(UserPreference(id=uuid.uuid4(), user_id=user.id, preference_key="notifications", preference_value=str(random.choice([True,False])), created_by="generate_user_preferences.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(prefs[:25])
    session.commit()
    print(f"✓ Inserted {len(prefs[:25])} user preferences")
    session.close()

if __name__ == "__main__":
    try: generate_user_preferences()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
