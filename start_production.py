#!/usr/bin/env python3
"""
Production startup script for Job Scraper
"""

import os
import sys
from web_app import app

if __name__ == '__main__':
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Get port from environment (Railway, Heroku, etc. set this)
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Starting Job Scraper in production mode on port {port}")
    
    # Start the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
