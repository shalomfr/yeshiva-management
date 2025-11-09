# -*- coding: utf-8 -*-
"""
Pywebview Wrapper - Run Yeshiva App as Desktop Application
Wrapper Pywebview - הפעלת אפליקציית ישיבה כאפליקציה שולחנית
"""

import sys
import threading
import time
from app import app

def run_flask():
    """Run Flask server in background"""
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)

def main():
    """Main entry point"""
    print("Starting Yeshiva Management System...")
    print("הפעלת מערכת ניהול ישיבה...")

    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Wait for Flask to start
    time.sleep(2)

    try:
        import webview
        webview.create_window(
            'מערכת ניהול ישיבה - Yeshiva Management System',
            'http://127.0.0.1:5000',
            width=1400,
            height=900,
            background_color='#E8F4F8'
        )
        webview.start()
    except ImportError:
        print("PyWebView not installed. Running Flask directly...")
        print("Open browser to: http://127.0.0.1:5000")
        flask_thread.join()

if __name__ == '__main__':
    main()
