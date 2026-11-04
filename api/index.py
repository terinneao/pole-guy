import sys
import os

# Ensure the root directory of the repository is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Expose the Flask WSGI application instance for Vercel Serverless Functions
from app import app
