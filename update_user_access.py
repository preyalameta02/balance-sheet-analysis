#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.getcwd())

from app.database import SessionLocal
from app.models import User

def update_user_access():
    """Update user's assigned companies"""
    db = SessionLocal()
    
    try:
        # Get the user
        user = db.query(User).filter(User.email == "test2@example.com").first()
        if user:
            # Update assigned companies to include company ID 1 (Jio Platforms)
            user.assigned_companies = [1]
            db.commit()
            print(f"✅ Updated user {user.email} with assigned companies: {user.assigned_companies}")
        else:
            print("❌ User not found")
            
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_access() 