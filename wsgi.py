"""
WSGI Production Entrypoint for Loan Approval Prediction System
Serves the Flask application using production WSGI servers such as Waitress or Gunicorn.
"""
import os
import sys

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app

# Application alias for WSGI servers
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    try:
        # Use Waitress if available (recommended on Windows & cross-platform)
        from waitress import serve
        print(f"[INFO] Starting production server with Waitress on http://127.0.0.1:{port} ...")
        serve(app, host="127.0.0.1", port=port)
    except ImportError:
        print(f"[INFO] Waitress not installed. Running standard server on http://127.0.0.1:{port} ...")
        app.run(host="127.0.0.1", port=port, debug=False)
