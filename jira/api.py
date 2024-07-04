from jira import JIRA
from config.config import JIRA_URL, AUTH

options = {
    'server': JIRA_URL
}

jira = JIRA(options, basic_auth=AUTH)