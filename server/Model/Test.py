import joblib
import subprocess
import numpy as np
import pandas as pd
from radon.complexity import cc_visit
import re

def load_model(file_name):
    """
    Load the trained model from a .pkl file.
    """
    try:
        model = joblib.load(file_name)
        print(f"Model loaded successfully from {file_name}!")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def extract_vulnerability_patterns(file_diff):
    """
    Extract features based on patterns in the file_diff.
    """
    return {
        "contains_sql_keywords": bool(re.search(r"\b(SELECT|INSERT|UPDATE|DELETE|WHERE|FROM|DROP|CREATE|EXECUTE)\b", file_diff, re.IGNORECASE)),
        "contains_command_injection": bool(re.search(r"\b(os\.system|subprocess\.call|subprocess\.Popen)\b", file_diff)),
        "contains_unsafe_deserialization": bool(re.search(r"\b(pickle\.load|yaml\.load)\b", file_diff)),
        "contains_hardcoded_credentials": bool(re.search(r"\b(password|passwd|key|secret|token|api_key)\b.*[=:].*['\"]", file_diff, re.IGNORECASE)),
        "contains_insecure_crypto": bool(re.search(r"\b(md5|sha1|des|rc4|base64\.decode)\b", file_diff, re.IGNORECASE)),
        "contains_buffer_operations": bool(re.search(r"\b(strcpy|strcat|gets|scanf|memcpy)\b", file_diff)),
        "contains_path_traversal": bool(re.search(r"(\.\.\\|\.\./|os\.path\.join|os\.open)", file_diff)),
        "contains_xss_patterns": bool(re.search(r"(<script>|document\.write|innerHTML|eval|alert)", file_diff, re.IGNORECASE)),
    }

def extract_commit_features(commit_hash, repository_path):
    """
    Extract features from a specific commit using Git and file analysis.
    """
    try:
        # Check if the commit has a parent
        parent_commit_check = subprocess.check_output(
            ['git', '-C', repository_path, 'rev-list', '--parents', '-n', '1', commit_hash]
        ).decode().strip().split()

        # If the commit has no parent, skip it
        if len(parent_commit_check) == 1:
            print(f"Skipping the first commit (no parent): {commit_hash}")
            return None

        # Get the diff stats for the commit
        diff_stats = subprocess.check_output(
            ['git', '-C', repository_path, 'diff', '--numstat', f'{commit_hash}~1', commit_hash]
        ).decode().strip().split("\n")

        # If no diff stats, skip the commit
        if not diff_stats:
            print(f"No changes detected for commit: {commit_hash}")
            return None

        num_lines_added = 0
        num_lines_deleted = 0

        # Parse diff stats
        for line in diff_stats:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    added = int(parts[0]) if parts[0] != '-' else 0
                    deleted = int(parts[1]) if parts[1] != '-' else 0
                    num_lines_added += added
                    num_lines_deleted += deleted
                except ValueError:
                    print(f"Skipping invalid diff stat line: {line}")
                    continue

        # Analyze complexity of modified files
        complexity = 0
        vulnerability_patterns = {
            "contains_sql_keywords": False,
            "contains_command_injection": False,
            "contains_unsafe_deserialization": False,
            "contains_hardcoded_credentials": False,
            "contains_insecure_crypto": False,
            "contains_buffer_operations": False,
            "contains_path_traversal": False,
            "contains_xss_patterns": False,
        }

        modified_files = subprocess.check_output(
            ['git', '-C', repository_path, 'diff', '--name-only', f'{commit_hash}~1', commit_hash]
        ).decode().strip().split("\n")

        for file in modified_files:
            # Skip binary files
            if file.endswith((".rar", ".7z")):
                print(f"Skipping binary file: {file}")
                continue

            # Analyze text-based files
            try:
                with open(f"{repository_path}/{file}", 'r') as f:
                    code = f.read()

                # Complexity analysis (only for Python)
                if file.endswith(".py"):
                    complexity += sum(c.complexity for c in cc_visit(code))

                # Extract pattern-based features
                file_patterns = extract_vulnerability_patterns(code)
                for key, value in file_patterns.items():
                    vulnerability_patterns[key] = vulnerability_patterns[key] or value

            except Exception as e:
                print(f"Error analyzing file {file}: {e}")

        # Example CVSS3 base score
        cvss3_base_score = min(10.0, complexity / 10.0)

        # If no valid text-based files were analyzed
        if complexity == 0 and num_lines_added == 0 and num_lines_deleted == 0:
            print(f"No analyzable files found in commit: {commit_hash}")
            return None

        commit_features = {
            "cvss3_base_score": cvss3_base_score,
            "num_lines_added": num_lines_added,
            "num_lines_deleted": num_lines_deleted,
            "file_complexity": complexity,
            **vulnerability_patterns
        }

        # Log extracted features
        print(f"Extracted features for commit {commit_hash}: {commit_features}")
        return commit_features

    except subprocess.CalledProcessError as e:
        print(f"Error extracting features for commit {commit_hash}: {e}")
        return None

def predict_commit_vulnerability(model, commit_features):
    """
    Predict whether a commit is vulnerable or non-vulnerable with adjusted thresholds and rule-based overrides.
    """
    model_features = [
        "cvss3_base_score", "num_lines_added", "num_lines_deleted", "file_complexity",
        "contains_sql_keywords", "contains_command_injection", "contains_unsafe_deserialization",
        "contains_hardcoded_credentials", "contains_insecure_crypto", "contains_buffer_operations",
        "contains_path_traversal", "contains_xss_patterns"
    ]

    features = pd.DataFrame([[commit_features.get(feature, 0) for feature in model_features]], columns=model_features)

    # Log features passed to the model
    print("Features passed to the model:")
    print(features)

    # Predict probabilities
    probabilities = model.predict_proba(features)
    print("Prediction probabilities:", probabilities)

    # Adjust threshold and add rule-based logic
    if probabilities[0][1] > 0.4 or commit_features["contains_sql_keywords"] or commit_features["contains_hardcoded_credentials"]:
        return "Vulnerable"
    else:
        return "Non-Vulnerable"

def main():
    """
    Main function to test the model on repository commits.
    """
    # Path to the trained model
    model_file = "trained_model.pkl"

    # Load the trained model
    model = load_model(model_file)
    if model is None:
        return

    # Local repository path
    repository_path = "C:/Users/UOG/Documents/GitHub/UnauthorizedAccessModel"

    # Get the last N commits
    num_commits_to_test = 10
    commit_hashes = subprocess.check_output(
        ['git', '-C', repository_path, 'log', '-n', str(num_commits_to_test), '--pretty=format:%H']
    ).decode().strip().split("\n")

    # Analyze commits
    for commit_hash in commit_hashes:
        print(f"\nAnalyzing commit: {commit_hash}")
        commit_features = extract_commit_features(commit_hash, repository_path)
        if commit_features:
            result = predict_commit_vulnerability(model, commit_features)
            print(f"Prediction for commit {commit_hash}: {result}")
        else:
            print(f"Could not extract features for commit {commit_hash}")

if __name__ == "__main__":
    main()
