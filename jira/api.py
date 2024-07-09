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
    
def fetch_issues(project_key, start_date, end_date):
    jql = f'project = {project_key} AND created >= "{start_date}" AND created <= "{end_date}"'
    fields = 'key,summary,status,assignee,worklog,timetracking'
    url = f"{JIRA_URL}/search?jql={jql}&fields={fields}"
    response = requests.get(url, auth=AUTH)

    if response.status_code == 200:
        issues = response.json().get('issues', [])
        return issues
    else:
        print(f"Failed to fetch issues: {response.status_code} - {response.text}")
        return None
