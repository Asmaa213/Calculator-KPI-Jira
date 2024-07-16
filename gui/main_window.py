import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import pandas as pd
import os
from jira.api import fetch_people_on_project, fetch_issues, fetch_changelog_for_issue 

class MainWindow:
    def __init__(self, projects):
        self.root = tk.Tk()
        self.root.title("Calculator KPI Jira")
        self.projects = projects  
        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        # Cadre principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both')

        # Créer un widget Notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both')

        # Créer les cadres pour les onglets
        self.tab_evolution = ttk.Frame(self.notebook)
        self.tab_correction = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_evolution, text="Evolution")
        self.notebook.add(self.tab_correction, text="Correction")

        # Ajouter du contenu à l'onglet "L'évolution"
        self.create_evolution_tab()

        # Ajouter du contenu à l'onglet "La correction"
        self.create_correction_tab()

    def create_evolution_tab(self):
        # Cadre pour les boutons spécifiques à l'onglet "L'évolution"
        self.button_frame_evolution = ttk.Frame(self.tab_evolution)
        self.button_frame_evolution.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.input_button_evolution = ttk.Button(self.button_frame_evolution, text="Refresh Information", command=self.open_input_window_evolution)
        self.input_button_evolution.pack(side=tk.LEFT, padx=5)

        self.export_button_evolution = ttk.Button(self.button_frame_evolution, text="Export to Excel", command=self.export_results)
        self.export_button_evolution.pack(side=tk.LEFT, padx=5)

        # Cadre principal de l'onglet évolution
        self.main_frame_evolution = ttk.Frame(self.tab_evolution)
        self.main_frame_evolution.pack(expand=True, fill='both', padx=5, pady=5)

        # Cadre de gauche pour les détails Jira
        self.left_frame_evolution = ttk.Frame(self.main_frame_evolution)
        self.left_frame_evolution.pack(side=tk.LEFT, expand=True, fill='both', padx=5, pady=5)

        self.filter_label1 = ttk.Label(self.left_frame_evolution, text="Jira details:")
        self.filter_label1.pack(anchor=tk.W, padx=5, pady=5)

        self.result_text1 = tk.Text(self.left_frame_evolution, height=20, width=80)
        self.result_text1.pack(anchor=tk.W, padx=5, pady=5, expand=True, fill=tk.BOTH)

        # Cadre de droite pour les détails d'efficience
        self.right_frame_evolution = ttk.Frame(self.main_frame_evolution)
        self.right_frame_evolution.pack(side=tk.RIGHT, fill='y', padx=5, pady=5)

        # Ajouter les champs d'efficience
        ttk.Label(self.right_frame_evolution, text="EFFICIENCY").pack(anchor=tk.W, padx=5, pady=5)

        labels = [
            "Cumulative Estimate (H)",
            "Cumulative Incurred (H) (Including Tasks Without Estimate)",
            "Cumulative Incurred (H) (Excluding Tasks Without Estimate)",
            "Cumulative Efficiency (H)",
            "Cumulative Efficiency (%)",
            "Number of Efficient Tasks",
            "Number of Inefficient Tasks",
            "Number of Unestimated Tasks"
        ]

        for label in labels:
            ttk.Label(self.right_frame_evolution, text=label).pack(anchor=tk.W, padx=5, pady=5)
            ttk.Entry(self.right_frame_evolution).pack(anchor=tk.W, padx=5, pady=5)

    def create_correction_tab(self):
        # Cadre pour les boutons spécifiques à l'onglet "La correction"
        self.button_frame_correction = ttk.Frame(self.tab_correction)
        self.button_frame_correction.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.input_button_correction = ttk.Button(self.button_frame_correction, text="Refresh Information", command=self.open_input_window_correction)
        self.input_button_correction.pack(side=tk.LEFT, padx=5)

        self.export_button_correction = ttk.Button(self.button_frame_correction, text="Export to Excel", command=self.export_results)
        self.export_button_correction.pack(side=tk.LEFT, padx=5)

        # Cadre principal de l'onglet correction
        self.main_frame_correction = ttk.Frame(self.tab_correction)
        self.main_frame_correction.pack(expand=True, fill='both', padx=5, pady=5)

        # Cadre de gauche pour les détails Jira
        self.left_frame_correction = ttk.Frame(self.main_frame_correction)
        self.left_frame_correction.pack(side=tk.LEFT, expand=True, fill='both', padx=5, pady=5)

        self.filter_label2 = ttk.Label(self.left_frame_correction, text="Jira errors:")
        self.filter_label2.pack(anchor=tk.W, padx=5, pady=5)

        # Création du Treeview pour afficher les issues
        self.issue_tree = ttk.Treeview(self.left_frame_correction, columns=("ID", "Summary", "Status", "Assignee", "Worklog", "Estimation", "ETC","Cause"), show='headings')
        self.issue_tree.heading("ID", text="ID")
        self.issue_tree.heading("Summary", text="Summary")
        self.issue_tree.heading("Status", text="Status")
        self.issue_tree.heading("Assignee", text="Assigned to")
        self.issue_tree.heading("Worklog", text="Worklog")
        self.issue_tree.heading("Estimation", text="Estimate")
        self.issue_tree.heading("ETC", text="ETC")
        self.issue_tree.heading("Cause", text="Cause")

        self.issue_tree.column("ID", width=100)
        self.issue_tree.column("Summary", width=250)
        self.issue_tree.column("Status", width=100)
        self.issue_tree.column("Assignee", width=100)
        self.issue_tree.column("Worklog", width=100)
        self.issue_tree.column("Estimation", width=100)
        self.issue_tree.column("ETC", width=100)
        self.issue_tree.column("Cause", width=300)

        self.issue_tree.pack(expand=True, fill='both', padx=5, pady=5)


    def open_input_window_correction(self):
        # Logique pour ouvrir une nouvelle fenêtre d'entrée des informations
        input_window = tk.Toplevel(self.root)
        input_window.title("Refresh Information")

        # Cadre pour les combobox
        combobox_frame = ttk.Frame(input_window)
        combobox_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        # Combobox pour les projets
        combobox_label2 = ttk.Label(combobox_frame, text="Projects:")
        combobox_label2.pack(side=tk.LEFT, padx=5, pady=5)

        project_names = [project['name'] for project in self.projects]
        self.combobox_project_var = tk.StringVar()
        combobox2 = ttk.Combobox(combobox_frame, textvariable=self.combobox_project_var, values=project_names, state='readonly')
        combobox2.pack(side=tk.LEFT, padx=5, pady=5)

        # Cadre pour les dates
        date_frame = ttk.Frame(input_window)
        date_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        date_label_start = ttk.Label(date_frame, text="Start Date:")
        date_label_start.pack(side=tk.LEFT, padx=5, pady=5)

        self.start_date_entry = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.pack(side=tk.LEFT, padx=5, pady=5)

        date_label_end = ttk.Label(date_frame, text="End Date:")
        date_label_end.pack(side=tk.LEFT, padx=5, pady=5)

        self.end_date_entry = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.pack(side=tk.LEFT, padx=5, pady=5)

        submit_button_correction = ttk.Button(input_window, text="Submit", command=lambda: self.submit_correction(input_window))
        submit_button_correction.pack(anchor=tk.W, padx=5, pady=5)

    def open_input_window_evolution(self):
        # Logique pour ouvrir une nouvelle fenêtre d'entrée des informations
        input_window1 = tk.Toplevel(self.root)
        input_window1.title("Refresh Information")

        # Cadre pour les combobox
        combobox_frame = ttk.Frame(input_window1)
        combobox_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        # Combobox pour les projets
        combobox_label2 = ttk.Label(combobox_frame, text="Projects:")
        combobox_label2.pack(side=tk.LEFT, padx=5, pady=5)

        project_names = [project['name'] for project in self.projects]
        self.combobox2 = ttk.Combobox(combobox_frame, values=project_names, state='readonly')
        self.combobox2.pack(side=tk.LEFT, padx=5, pady=5)
        self.combobox2.bind("<<ComboboxSelected>>", self.update_user_combobox)  

        # Combobox pour le nom d'utilisateur
        combobox_label = ttk.Label(combobox_frame, text="Users full name:")
        combobox_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.combobox = ttk.Combobox(combobox_frame, state='readonly')  
        self.combobox.pack(side=tk.LEFT, padx=5, pady=5)

        # Cadre pour les dates
        date_frame = ttk.Frame(input_window1)
        date_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        date_label_start = ttk.Label(date_frame, text="Start Date:")
        date_label_start.pack(side=tk.LEFT, padx=5, pady=5)

        self.date_start = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_start.pack(side=tk.LEFT, padx=5, pady=5)

        date_label_end = ttk.Label(date_frame, text="End Date:")
        date_label_end.pack(side=tk.LEFT, padx=5, pady=5)

        self.date_end = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_end.pack(side=tk.LEFT, padx=5, pady=5)

        submit_button_evolution = ttk.Button(input_window1, text="Submit", command=self.submit_evolution)
        submit_button_evolution.pack(anchor=tk.W, padx=5, pady=5)

    def update_user_combobox(self, event):
        project_name = self.combobox2.get()
        selected_project = next((project for project in self.projects if project['name'] == project_name), None)

        if selected_project:
            project_key = selected_project['key']
            people = fetch_people_on_project(project_key)

            if people:
                user_names = [person['displayName'] for person in people]
                self.combobox['values'] = user_names
                self.combobox.set('')  
            else:
                messagebox.showerror("Error", "Unable to retrieve people for this project")
        else:
            messagebox.showerror("Error", "Project not found")

    def submit_evolution(self):
        # Logique pour le bouton "Submit" de l'onglet "L'evolution"
        selected_user = self.combobox.get()
        start_date = self.date_start.get()
        end_date = self.date_end.get()

        messagebox.showinfo("Submit", "Evolution submitted")


    def submit_correction(self, input_window):
        selected_project = self.combobox_project_var.get()
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        # Vider le tableau existant
        for i in self.issue_tree.get_children():
            self.issue_tree.delete(i)

        issues = fetch_issues(selected_project, start_date, end_date)
        
        if not issues:
            messagebox.showerror("Error", "No issues found for the selected project and date range.")
            return

        # Filtrer et remplir le tableau avec les nouvelles issues
        for issue in issues:
            issue_id = issue['key']
            issue_summary = issue['fields']['summary']
            issue_status = issue['fields']['status']['name']
            issue_assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'

            causes = []

            # Condition 1: Issues sans estimation
            if 'timetracking' in issue['fields'] and 'originalEstimateSeconds' not in issue['fields']['timetracking'] :
                causes.append("Issue without estimate")

            # Condition 2: Issues avec un worklog différent de 0 et status open
            if issue_status == 'Open' and 'worklog' in issue['fields'] and 'worklogs' in issue['fields']['worklog']:
                total_time_spent = sum(entry['timeSpentSeconds'] for entry in issue['fields']['worklog']['worklogs'])
                if total_time_spent > 0:
                    causes.append("Issue with worklog and status Open")

            # Condition 3: Issues sans worklog et status différent de open
            if issue_status != 'Open' and ('worklog' not in issue['fields'] or 'worklogs' not in issue['fields']['worklog'] or sum(entry['timeSpentSeconds'] for entry in issue['fields']['worklog']['worklogs']) == 0):
                causes.append("Issue without worklog and status different from Open")
            
            # Condition 4: Issues livrées (statut = Done) avec ETC différent de 0
            if issue_status == 'Done' and 'timetracking' in issue['fields'] and 'remainingEstimateSeconds' in issue['fields']['timetracking']:
                if issue['fields']['timetracking']['remainingEstimateSeconds'] != 0:
                    causes.append("Delivered issue with ETC different from 0")
            
            # Condition 5: Issues dont le statut est différent de done et ETC = 0
            if issue_status != 'Done' and 'timetracking' in issue['fields'] and 'remainingEstimateSeconds' in issue['fields']['timetracking']:
                if issue['fields']['timetracking']['remainingEstimateSeconds'] == 0:
                    causes.append("Undelivered issue with ETC = 0")
            
            # Condition 6: Issues dont plusieurs personnes ont modifié dans le même worklog
            worklog_authors = set()
            if 'worklog' in issue['fields'] and 'worklogs' in issue['fields']['worklog']:
                worklog_authors.update(entry['author']['displayName'] for entry in issue['fields']['worklog']['worklogs'])

            changelog = fetch_changelog_for_issue(issue_id)

            if changelog:
                print("Changelog trouvé!")
                changelog_authors = {entry['author']['displayName'] for entry in changelog['histories']}
                worklog_authors.update(changelog_authors)
            else:
                print("Le changelog n'a pas été trouvé dans l'issue")

            if len(worklog_authors) > 1:
                causes.append("Issue with modifications by multiple users")
            
            print("Auteurs du worklog :", worklog_authors)

            if not causes:
                continue

            # Estimation d'origine
            if 'timetracking' in issue['fields'] and 'originalEstimateSeconds' in issue['fields']['timetracking']:
                issue_estimation = issue['fields']['timetracking']['originalEstimateSeconds'] / 3600  
            else:
                issue_estimation = 0

            # ETC (estimate to complete)
            if 'timetracking' in issue['fields'] and 'remainingEstimateSeconds' in issue['fields']['timetracking']:
                issue_etc = issue['fields']['timetracking']['remainingEstimateSeconds'] / 3600  
            else:
                issue_etc = 0

            # Worklog (temps passé)
            if 'worklog' in issue['fields'] and 'worklogs' in issue['fields']['worklog']:
                total_time_spent = sum(entry['timeSpentSeconds'] for entry in issue['fields']['worklog']['worklogs']) / 3600  
            else:
                total_time_spent = 0

            # Insérer l'issue avec ses détails et les causes spécifiques
            for cause in causes:
                self.issue_tree.insert("", "end", values=(issue_id, issue_summary, issue_status, issue_assignee, total_time_spent, issue_estimation, issue_etc, cause))

        input_window.destroy()

    def export_results(self):
        # Logique pour exporter les résultats
        file_path = os.path.join(os.path.expanduser("~"), "jira_results.xlsx")
        data = []
        for i in self.issue_tree.get_children():
            item_values = self.issue_tree.item(i, 'values')
            data.append(item_values)

        df = pd.DataFrame(data,
                        columns=["ID", "Summary", "Status", "Assignee", "Worklog", "Estimation", "ETC", "Cause"])

        try:
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            print("Data exported successfully.")
        except Exception as e:
            print(f"Failed to export data: {e}")

    def run(self):
        self.root.mainloop()
