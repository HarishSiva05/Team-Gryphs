from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from commit_activity.activity import CommitsActivity
from datetime import datetime
import hmac
import hashlib
import json
import queue
import requests
import pickle
import os
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, f_classif
import base64
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

WEBHOOK_SECRET = "`123asd`123"
GITHUB_TOKEN = "env"
GITHUB_ORG = "NIXE05"

event_queue = queue.Queue()
commits_activity = CommitsActivity()

def load_model(file_path):
    try:
        with open(file_path, 'rb') as file:
            model = pickle.load(file)
        print(f"Successfully loaded model from {file_path}")
        return model
    except FileNotFoundError:
        print(f"Error: Model file not found at {file_path}")
    except pickle.UnpicklingError:
        print(f"Error: Unable to unpickle model at {file_path}")
    except Exception as e:
        print(f"Error loading model from {file_path}: {str(e)}")
    return None

current_dir = os.path.dirname(os.path.abspath(__file__))
unusual_hours_model_path = os.path.join(current_dir, 'model', 'unusual_hours_model.pkl')
vulnerability_model_path = os.path.join(current_dir, 'model', 'vulnerability_model.pkl')

unusual_hours_model = load_model(unusual_hours_model_path)
vulnerability_model = load_model(vulnerability_model_path)

if unusual_hours_model is None:
    print("Warning: Unusual hours model could not be loaded. Unusual commit time detection will be disabled.")

if vulnerability_model is None:
    print("Warning: Vulnerability model could not be loaded. Vulnerability detection will be disabled.")

def convert_to_serializable(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    return obj

def preprocess_commit_time(commit_time, commit_info):
    dt = datetime.fromisoformat(commit_time.replace('Z', '+00:00'))
    
    access_hour = dt.hour
    hour = dt.hour
    day_of_week = dt.weekday()
    month = dt.month
    day = dt.day
    year = dt.year

    language = 'unknown'
    mode = 'unknown'
    repository = commit_info['repo']
    repository_risk = 0
    unusual_hour = 0
    mode_category = 'unknown'

    language_map = {'unknown': 0, 'python': 1, 'javascript': 2}
    mode_map = {'unknown': 0, 'normal': 1, 'maintenance': 2}
    repository_map = {repository: 1}
    mode_category_map = {'unknown': 0, 'development': 1, 'operations': 2}

    features = [
        access_hour,
        hour,
        day_of_week,
        language_map.get(language, 0),
        month,
        mode_map.get(mode, 0),
        day,
        repository_map.get(repository, 0),
        year,
        repository_risk,
        unusual_hour,
        mode_category_map.get(mode_category, 0)
    ]
    
    return np.array(features).reshape(1, -1)

def calculate_complexity(code):
    lines = code.split('\n')
    return sum(len(line.strip()) for line in lines)

def preprocess_commit_for_vulnerability(commit_info):
    features = [
        len(commit_info['message']),
        commit_info['message'].count('fix'),
        commit_info['message'].count('vulnerability'),
        commit_info['message'].count('security'),
        len(commit_info['message'].split()),
        int('bug' in commit_info['message'].lower()),
        int('patch' in commit_info['message'].lower()),
        int('update' in commit_info['message'].lower()),
        commit_info.get('num_lines_added', 0),
        commit_info.get('num_lines_deleted', 0),
        commit_info.get('dmm_unit_complexity', 0),
        commit_info.get('dmm_unit_size', 0),
    ]
    
    code = commit_info.get('code_after', '')
    features.extend([
        int(bool(re.search(r"SELECT.*FROM.*WHERE.*=\s*'.*'", code))),
        int(bool(re.search(r"execute$$.*\+.*$$", code))),
        int(bool(re.search(r"cursor\.execute\(f[\"']", code))),
        code.count('sqlite3'),
        code.count('mysql'),
        code.count('psycopg2'),
    ])
    
    vectorizer = CountVectorizer(max_features=100)
    text_features = vectorizer.fit_transform([commit_info['message'] + ' ' + code]).toarray()[0]
    
    features.extend(text_features)
    
    features = np.array(features).reshape(1, -1)
    
    scaler = StandardScaler()
    features = scaler.fit_transform(features)
    
    return features

def select_features(X, k=12):
    selector = SelectKBest(score_func=f_classif, k=k)
    return selector.fit_transform(X, [0])  # We don't have labels, so use a dummy label

def is_unusual_commit_time(commit_time, commit_info):
    if unusual_hours_model is None:
        print("Warning: Unusual hours model not loaded. Unable to predict unusual commit times.")
        return False
    processed_time = preprocess_commit_time(commit_time, commit_info)
    prediction = unusual_hours_model.predict(processed_time)
    return bool(prediction[0])

def detect_vulnerability(commit_info):
    code = commit_info.get('code_after', '')
    message = commit_info['message'].lower()
    
    print(f"Analyzing commit: {message}")
    print(f"Code content: {code[:100]}...")  # Print first 100 characters of code
    
    # Rule-based checks
    sql_injection_patterns = [
        r"SELECT.*FROM.*WHERE.*=\s*'.*'",
        r"execute$$.*\+.*$$",
        r"cursor\.execute\(f[\"']"
    ]
    if any(re.search(pattern, code) for pattern in sql_injection_patterns):
        print("SQL injection vulnerability detected")
        return True
    
    vulnerable_functions = ['eval(', 'exec(', 'os.system(', 'subprocess.call(']
    if any(func in code for func in vulnerable_functions):
        print("Vulnerable function detected")
        return True
    
    if 'md5' in code or 'sha1' in code:
        print("Weak cryptography detected")
        return True
    
    security_terms = ['sql injection', 'xss', 'cross-site scripting', 'remote code execution', 'cve']
    if any(term in message for term in security_terms):
        print("Security-related term detected in commit message")
        return True
    
    # Machine learning-based check
    if vulnerability_model:
        processed_commit = preprocess_commit_for_vulnerability(commit_info)
        
        # Select the top k features (where k is the number of features the model expects)
        expected_features = vulnerability_model.n_features_in_
        selected_features = select_features(processed_commit, k=expected_features)
        
        prediction = vulnerability_model.predict_proba(selected_features)
        vulnerability_score = prediction[0][1]  # Assuming 1 is the "vulnerable" class
        print(f"Vulnerability score: {vulnerability_score}")
        if vulnerability_score > 0.5:  # Adjust this threshold as needed
            print("Machine learning model detected potential vulnerability")
            return True
    
    print("No vulnerability detected")
    return False

def verify_signature(payload_body, signature):
    expected_signature = 'sha1=' + hmac.new(WEBHOOK_SECRET.encode(), payload_body, hashlib.sha1).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def get_all_repositories():
    url = f"https://api.github.com/users/{GITHUB_ORG}/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repos = response.json()
        return [repo['name'] for repo in repos]
    else:
        app.logger.error(f"Failed to fetch repositories: {response.status_code}")
        return []

def get_latest_commits(repo_name, count=5):
    url = f"https://api.github.com/repos/{GITHUB_ORG}/{repo_name}/commits"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"per_page": count}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        commits = response.json()
        return [
            {
                "type": "commit",
                "repo": repo_name,
                "pusher": commit["commit"]["author"]["name"],
                "message": commit["commit"]["message"],
                "timestamp": commit["commit"]["author"]["date"]
            }
            for commit in commits
        ]
    else:
        app.logger.error(f"Failed to fetch commits for {repo_name}: {response.status_code}")
        return []

# Placeholder functions for Kestra interaction.  Replace with your actual implementation.
def trigger_kestra_workflow():
    # Your code to trigger the Kestra workflow here.  Should return the execution ID.
    print("Triggering Kestra workflow...")
    # Example:  Replace with your actual Kestra API call
    # response = requests.post("your_kestra_api_url", data={"some": "data"})
    # return response.json().get("executionId")
    return "kestra_execution_id_123" # Replace with actual execution ID


def check_workflow_status(execution_id):
    # Your code to check the Kestra workflow status here.
    print(f"Checking Kestra workflow status for execution ID: {execution_id}...")
    # Example: Replace with your actual Kestra API call
    # response = requests.get(f"your_kestra_api_url/{execution_id}/status")
    # return response.json().get("status")
    # Simulate different statuses for testing
    statuses = ["RUNNING", "RUNNING", "RUNNING", "SUCCESS"]
    return statuses[min(len(statuses)-1, int(execution_id[-3:]))]


@app.route('/webhook', methods=['POST'])
def github_webhook():
    print("Received webhook event")
    signature = request.headers.get('X-Hub-Signature')
    if not signature or not verify_signature(request.data, signature):
        print("Signature verification failed")
        return jsonify({"error": "Invalid signature"}), 403

    event = request.headers.get('X-GitHub-Event')
    payload = request.json
    print(f"Received {event} event")

    if event == 'push':
        repo = payload['repository']['name']
        owner = payload['repository']['owner']['name']
        commits = payload['commits']
        
        print(f"Processing {len(commits)} commits")
        for commit in commits:
            commit_sha = commit['id']
            modified_files = commit.get('modified', [])
            
            for file_path in modified_files:
                file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={commit_sha}"
                headers = {
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                }
                response = requests.get(file_url, headers=headers)
                
                if response.status_code == 200:
                    file_content = base64.b64decode(response.json()['content']).decode('utf-8')
                    
                    commit_info = {
                        'repo': repo,
                        'pusher': commit['author']['name'],
                        'message': commit['message'],
                        'timestamp': commit['timestamp'],
                        'code_after': file_content,
                        'num_lines_added': commit.get('stats', {}).get('additions', 0),
                        'num_lines_deleted': commit.get('stats', {}).get('deletions', 0),
                        'dmm_unit_complexity': 0,
                        'dmm_unit_size': 0,
                        'file_complexity': calculate_complexity(file_content),
                        'programming_language': '',
                        'cvss3_base_score': 0,
                        'cwe_name': '',
                        'vulnerability_description': '',
                    }
                    
                    print(f"Processing commit: {commit_info['message'][:100]}...")
                    
                    is_unusual = is_unusual_commit_time(commit['timestamp'], commit_info)
                    is_vulnerable = detect_vulnerability(commit_info)
                    
                    commit_info.update({
                        'type': 'commit',
                        'isUnusual': is_unusual,
                        'isVulnerable': is_vulnerable
                    })
                    
                    event_queue.put(commit_info)
                    print(f"Commit processed: isUnusual={is_unusual}, isVulnerable={is_vulnerable}")
                    
                    if is_unusual or is_vulnerable:
                        # Trigger Kestra workflow
                        execution_id = trigger_kestra_workflow()
                        if execution_id:
                            # Poll for workflow completion
                            while True:
                                status = check_workflow_status(execution_id)
                                print(f"Kestra workflow status: {status}")
                                if status in ['SUCCESS', 'FAILED']:
                                    break
                                time.sleep(5)  # Wait for 5 seconds before checking again
                            
                            # Add Kestra workflow result to event queue
                            kestra_result = {
                                'type': 'kestra_result',
                                'execution_id': execution_id,
                                'status': status,
                                'commit_info': commit_info
                            }
                            event_queue.put(kestra_result)
                            print(f"Kestra workflow result added to queue: {kestra_result}")
                    
                    if is_unusual:
                        alert_info = {
                            'type': 'alert',
                            'message': f"Unusual commit detected at {commit['timestamp']} by {commit['author']['name']} in {repo}"
                        }
                        event_queue.put(alert_info)
                        print(f"Unusual commit alert added to queue: {alert_info}")
                    
                    if is_vulnerable:
                        alert_info = {
                            'type': 'alert',
                            'message': f"Potential vulnerability detected in commit at {commit['timestamp']} by {commit['author']['name']} in {repo}"
                        }
                        event_queue.put(alert_info)
                        print(f"Vulnerability alert added to queue: {alert_info}")
                else:
                    print(f"Failed to fetch file contents for {file_path}: {response.status_code}")
    
    return jsonify({"status": "success"}), 200

@app.route('/events', methods=['GET'])
def events():
    def generate():
        while True:
            try:
                event = event_queue.get(timeout=30)
                serializable_event = convert_to_serializable(event)
                yield f"data: {json.dumps(serializable_event)}\n\n"
                print(f"Event sent to client: {serializable_event}")
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
                print("Keepalive sent to client")

    return Response(generate(), content_type='text/event-stream')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    
    if "date" in user_input.lower():
        current_date = datetime.now().strftime("%Y-%m-%d")
        return jsonify({'response': f"Today's date is {current_date}"})
    
    if "commit" in user_input.lower():
        repos = get_all_repositories()
        specific_repo = next((repo for repo in repos if repo.lower() in user_input.lower()), None)
        
        if specific_repo:
            commits = get_latest_commits(specific_repo)
            if commits:
                commit_messages = "\n".join([f"- {commit['message']} by {commit['pusher']} on {commit['timestamp']}" for commit in commits])
                return jsonify({'response': f"Here are the latest commits for the {specific_repo} repository:\n{commit_messages}"})
            else:
                return jsonify({'response': f"I couldn't fetch any commits for the {specific_repo} repository. Please try again later."})
        else:
            all_commits = []
            for repo in repos:
                commits = get_latest_commits(repo)
                all_commits.extend(commits)
            
            if all_commits:
                commit_messages = "\n".join([f"- [{commit['repo']}] {commit['message']} by {commit['pusher']} on {commit['timestamp']}" for commit in all_commits])
                return jsonify({'response': f"Here are the latest commits across all repositories:\n{commit_messages}"})
            else:
                return jsonify({'response': "I couldn't fetch any commits. Please try again later."})
    
    if "vulnerability" in user_input.lower() or "vulnerabilities" in user_input.lower():
        return jsonify({'response': "I'm monitoring commits for potential vulnerabilities. If any are detected, I'll raise an alert. For detailed vulnerability information, please check the security dashboard or consult with the security team."})
    
    try:
        response = commits_activity.get_answer(user_input)
        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({'response': "I'm sorry, I encountered an error while processing your request. Please try again."}), 500

@app.route('/', methods=['GET'])
def home():
    return "GitHub Webhook and Chat Server is running!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

