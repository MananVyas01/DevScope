1| """Simple test for the DevScope API."""
2| 
3| import asyncio
4| import sys
5| import os
6| 
7| # Add the backend directory to Python path
8| sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
9| 
10| async def test_basic_import():
11|     """Test basic imports work."""
12|     try:
13|         from app.config import settings
14|         print("✅ Config imported successfully")
15|         print(f"   Environment: {settings.ENVIRONMENT}")
16|         print(f"   Database URL: {settings.DATABASE_URL}")
17|         
18|         from app.models.database import init_db
19|         print("✅ Database models imported successfully")
20|         
21|         from app.api.v1.api import api_router
22|         print("✅ API router imported successfully")
23|         
24|         from app.main import app
25|         print("✅ FastAPI app imported successfully")
26|         print(f"   App title: {app.title}")
27|         
28|         return True
29|     except Exception as e:
30|         print(f"❌ Import failed: {e}")
31|         import traceback
32|         traceback.print_exc()
33|         return False
34| 
35| async def test_database_initialization():
36|     """Test database initialization."""
37|     try:
38|         from app.models.database import init_db, engine
39|         
40|         print("🔧 Initializing database...")
41|         await init_db()
42|         print("✅ Database initialized successfully")
43| 
44|         # Test connection
45|         async with engine.begin() as conn:
46|             await conn.execute("SELECT 1")  # Removed unused 'result' variable
47|             print("✅ Database connection test successful")
48| 
49|         return True
50|     except Exception as e:
51|         print(f"❌ Database initialization failed: {e}")
52|         import traceback
53|         traceback.print_exc()
54|         return False
55| 
56| async def main():
57|     """Run all tests."""
58|     print("🚀 DevScope API Test Suite")
59|     print("=" * 40)
60| 
61|     # Test imports
62|     print("\n📦 Testing Imports...")
63|     imports_ok = await test_basic_import()
64|     if not imports_ok:
65|         print("❌ Import tests failed, skipping database tests")
66|         return
67| 
68|     # Test database
69|     print("\n🗄️  Testing Database...")
70|     db_ok = await test_database_initialization()
71|     if imports_ok and db_ok:
72|         print("\n🎉 All tests passed! The API is ready to run.")
73|         print("\n💡 To start the server, run:")
74|         print("   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")  # Fixed indentation
75|     else:
76|         print("\n❌ Some tests failed. Please check the errors above.")
77| 
78| if __name__ == "__main__":
79|     asyncio.run(main())
80| 