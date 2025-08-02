#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.getcwd())

from app.database import SessionLocal
from app.models import User

def fix_user_role():
    """Update user role to ambani_family for testing"""
    db = SessionLocal()
    
    try:
        # Get the user by email
        user = db.query(User).filter(User.email == "test2@example.com").first()
        if user:
            # Update role to ambani_family
            user.role = "ambani_family"
            db.commit()
            print(f"✅ Updated user {user.email} role to: {user.role}")
        else:
            print("❌ User not found")
            
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_role() 