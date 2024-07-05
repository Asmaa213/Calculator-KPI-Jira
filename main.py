from gui.main_window import MainWindow
from jira.api import fetch_all_projects

if __name__ == "__main__":
    projects = fetch_all_projects()
    if projects:
        for project in projects:
            print(f"Project Key: {project['key']}, Project Name: {project['name']}")

    app = MainWindow(projects)

    app.run()