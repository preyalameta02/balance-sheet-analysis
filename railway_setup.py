#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from app.database import engine
    from app.models import Base
    
    print("🔧 Setting up database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("📋 Tables created:")
    print("   - users")
    print("   - companies") 
    print("   - balance_sheet_entries")
    print("   - raw_documents")
    print("\n🎉 Your database is ready for use!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all dependencies are installed")
except Exception as e:
    print(f"❌ Error creating database tables: {e}") 