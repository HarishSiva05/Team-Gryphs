YT Link - https://youtu.be/VLASBfyRqN8

Drive Link - https://drive.google.com/file/d/1xz9tdSRK6A0UK4eZENWa8Z5eNCpGuzlG/view?usp=share_link

# Description

Repository Security Assistant is a comprehensive security tool designed to safeguard GitHub repositories through real-time monitoring and advanced vulnerability detection. This containerized application combines a Python/Flask backend with a React frontend, utilizing machine learning models for identifying potential security risks and unusual commit patterns. Key features include real-time commit analysis via GitHub webhooks, an interactive chat interface for querying repository information. The system employs Llama models for natural language processing tasks, enhancing its ability to understand and respond to user queries about security concerns. For local testing and development, ngrok is used to expose the local server to the internet, allowing for seamless webhook integration with GitHub. This project aims to provide development teams with a powerful, user-friendly tool to maintain high security standards in their GitHub projects, offering real-time alerts, vulnerability assessments, and automated security workflows in a scalable, Docker-based environment. And we also aim to extend this to all online repositories 

NOTE - We used ChatGPT to refractor some of our code.

# Features

* Real-time monitoring of GitHub repositories
* Integration with Kestra for workflow orchestration
* Python-based data processing and API interactions
* Chatbot interface for delivering instant notifications
* Customizable alert system for different types of GitHub events

# Configuration

Open config.yml and update the following settings:

* GitHub repository details (owner, repo name)
* Kestra workflow configurations
* Chatbot integration details
* Customize the process_updates function in github_updates.py to handle the GitHub events according to your needs.

# Contact

If you have any questions or feedback, please contact at [nixe.cxt@gmail.com].


