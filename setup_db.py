#!/usr/bin/env python3

from app.database import engine
from app.models import Base

def setup_database():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("📋 Tables created:")
        print("   - users")
        print("   - companies") 
        print("   - balance_sheet_entries")
        print("   - raw_documents")
        print("\n🎉 Your database is ready for use!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

if __name__ == "__main__":
    setup_database() 