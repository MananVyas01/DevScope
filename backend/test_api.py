"""Simple test for the DevScope API."""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_basic_import():
    """Test basic imports work."""
    try:
        from app.config import settings
        print("✅ Config imported successfully")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Database URL: {settings.DATABASE_URL}")
        
        from app.models.database import init_db
        print("✅ Database models imported successfully")
        
        from app.api.v1.api import api_router
        print("✅ API router imported successfully")
        
        from app.main import app
        print("✅ FastAPI app imported successfully")
        print(f"   App title: {app.title}")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_initialization():
    """Test database initialization."""
    try:
        from app.models.database import init_db, engine
        
        print("🔧 Initializing database...")
        await init_db()
        print("✅ Database initialized successfully")
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ Database connection test successful")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 DevScope API Test Suite")
    print("=" * 40)
    
    # Test imports
    print("\n📦 Testing Imports...")
    imports_ok = await test_basic_import()
    
    if not imports_ok:
        print("❌ Import tests failed, skipping database tests")
        return
    
    # Test database
    print("\n🗄️  Testing Database...")
    db_ok = await test_database_initialization()
    
    if imports_ok and db_ok:
        print("\n🎉 All tests passed! The API is ready to run.")
        print("\n💡 To start the server, run:")
        print("   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
