#!/usr/bin/env python3
"""
Простой веб-сервер для просмотра логов и статуса
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class LogHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Agilite Scraper Status</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .success { background-color: #d4edda; color: #155724; }
                    .error { background-color: #f8d7da; color: #721c24; }
                    .info { background-color: #d1ecf1; color: #0c5460; }
                    pre { background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }
                    button { padding: 10px 20px; margin: 5px; cursor: pointer; }
                </style>
                <script>
                    function refreshLogs() {
                        location.reload();
                    }
                    function runTest() {
                        fetch('/run_test', {method: 'POST'})
                            .then(response => response.text())
                            .then(data => {
                                document.getElementById('test-output').innerHTML = '<pre>' + data + '</pre>';
                            });
                    }
                    setInterval(refreshLogs, 10000); // Refresh every 10 seconds
                </script>
            </head>
            <body>
                <h1>Agilite Scraper Status</h1>
                <button onclick="refreshLogs()">Refresh</button>
                <button onclick="runTest()">Run Test</button>
                <div id="test-output"></div>
                <h2>Environment Info</h2>
                <div class="info">
                    <strong>Python Version:</strong> {python_version}<br>
                    <strong>Working Directory:</strong> {cwd}<br>
                    <strong>PYTHONPATH:</strong> {pythonpath}<br>
                    <strong>DISPLAY:</strong> {display}<br>
                    <strong>Current Time:</strong> {current_time}
                </div>
                <h2>File Status</h2>
                {file_status}
                <h2>Import Test</h2>
                {import_status}
            </body>
            </html>
            """
            
            # Get environment info
            python_version = sys.version
            cwd = os.getcwd()
            pythonpath = os.environ.get('PYTHONPATH', 'Not set')
            display = os.environ.get('DISPLAY', 'Not set')
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Check files
            file_status = ""
            files_to_check = [
                'src/main.py',
                'src/data_collection/scraper_primary.py',
                'src/data_processing/data_processor.py',
                'requirements.txt'
            ]
            
            for file_path in files_to_check:
                if os.path.exists(file_path):
                    file_status += f'<div class="success">✓ {file_path} exists</div>'
                else:
                    file_status += f'<div class="error">✗ {file_path} does not exist</div>'
            
            # Test imports
            import_status = ""
            try:
                import requests
                import_status += '<div class="success">✓ requests imported</div>'
            except Exception as e:
                import_status += f'<div class="error">✗ requests: {e}</div>'
            
            try:
                import pandas as pd
                import_status += '<div class="success">✓ pandas imported</div>'
            except Exception as e:
                import_status += f'<div class="error">✗ pandas: {e}</div>'
            
            try:
                import schedule
                import_status += '<div class="success">✓ schedule imported</div>'
            except Exception as e:
                import_status += f'<div class="error">✗ schedule: {e}</div>'
            
            try:
                import selenium
                import_status += '<div class="success">✓ selenium imported</div>'
            except Exception as e:
                import_status += f'<div class="error">✗ selenium: {e}</div>'
            
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from data_collection.scraper_primary import AgiliteScraper
                import_status += '<div class="success">✓ AgiliteScraper imported</div>'
            except Exception as e:
                import_status += f'<div class="error">✗ AgiliteScraper: {e}</div>'
            
            try:
                from data_processing.data_processor import AgiliteDataProcessor
                import_status += '<div class="success">✓ AgiliteDataProcessor imported</div>'
            except Exception as e:
                import_status += f'<div class="error">✗ AgiliteDataProcessor: {e}</div>'
            
            html = html.format(
                python_version=python_version,
                cwd=cwd,
                pythonpath=pythonpath,
                display=display,
                current_time=current_time,
                file_status=file_status,
                import_status=import_status
            )
            
            self.wfile.write(html.encode())
            
        elif self.path == '/run_test':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            # Run the simple test
            try:
                result = subprocess.run([sys.executable, 'src/simple_test.py'], 
                                      capture_output=True, text=True, timeout=30)
                output = result.stdout + result.stderr
                self.wfile.write(output.encode())
            except Exception as e:
                self.wfile.write(f"Error running test: {e}".encode())
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'environment': {
                    'PYTHONPATH': os.environ.get('PYTHONPATH'),
                    'DISPLAY': os.environ.get('DISPLAY')
                },
                'files': {},
                'imports': {}
            }
            
            # Check files
            files_to_check = [
                'src/main.py',
                'src/data_collection/scraper_primary.py',
                'src/data_processing/data_processor.py',
                'requirements.txt'
            ]
            
            for file_path in files_to_check:
                status['files'][file_path] = os.path.exists(file_path)
            
            # Test imports
            try:
                import requests
                status['imports']['requests'] = True
            except:
                status['imports']['requests'] = False
            
            try:
                import pandas
                status['imports']['pandas'] = True
            except:
                status['imports']['pandas'] = False
            
            try:
                import schedule
                status['imports']['schedule'] = True
            except:
                status['imports']['schedule'] = False
            
            try:
                import selenium
                status['imports']['selenium'] = True
            except:
                status['imports']['selenium'] = False
            
            self.wfile.write(json.dumps(status, indent=2).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

def run_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), LogHandler)
    print(f"Starting web server on port {port}")
    print(f"Visit http://localhost:{port} to see status")
    server.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    run_server(port) 