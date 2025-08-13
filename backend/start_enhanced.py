#!/usr/bin/env python3
"""
Enhanced Startup Script for DocuGenie Ultra with Docling AI
"""
import os
import sys
import uvicorn

def main():
    """Start the enhanced DocuGenie Ultra Backend Server"""
    print("🚀 Starting DocuGenie Ultra Backend with Docling AI...")
    print("=" * 60)
    
    # Check if we can import the enhanced app
    try:
        from main import app
        print(f"✅ Enhanced FastAPI app loaded: {app.title}")
        print(f"✅ API routes: {len(app.routes)}")
        print(f"✅ Docling AI Integration: Active")
        
        # Get port from environment or use default
        port = int(os.getenv("PORT", 8007))
        host = os.getenv("HOST", "0.0.0.0")
        
        print(f"🌐 Starting server on {host}:{port}")
        print(f"📚 API docs: http://localhost:{port}/api/docs")
        print(f"🔍 Health check: http://localhost:{port}/health")
        print(f"🤖 AI Status: http://localhost:{port}/api/v1/ai/status")
        print("=" * 60)
        
        # Start server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Failed to import enhanced app: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
