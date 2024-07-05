import requests
from config.config import JIRA_URL, AUTH

def fetch_all_projects():
    url = f"{JIRA_URL}/project"
    response = requests.get(url, auth=AUTH)

    if response.status_code == 200:
        projects = response.json()
        return projects
    else:
        print(f"Failed to fetch projects: {response.status_code} - {response.text}")
        return None
    
def fetch_people_on_project(project_key):
    url = f"{JIRA_URL}/user/assignable/search?project={project_key}"
    response = requests.get(url, auth=AUTH)

    if response.status_code == 200:
        people = response.json()
        return people
    else:
        print(f"Failed to fetch people on project {project_key}: {response.status_code} - {response.text}")
        return None