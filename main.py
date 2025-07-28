import os
import json
import logging
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from scanner import SecurityScanner
from gemini_analyzer import GeminiAnalyzer
from email_reporter import EmailReporter

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "darkhunter-ai-secret-key")

# Initialize components
scanner = SecurityScanner()
analyzer = GeminiAnalyzer()
email_reporter = EmailReporter()

def load_scan_logs():
    """Load scan logs from JSON file"""
    try:
        with open('scan_logs.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_scan_log(log_entry):
    """Save scan log entry to JSON file"""
    logs = load_scan_logs()
    logs.append(log_entry)
    
    # Keep only last 100 entries
    if len(logs) > 100:
        logs = logs[-100:]
    
    with open('scan_logs.json', 'w') as f:
        json.dump(logs, f, indent=2)
