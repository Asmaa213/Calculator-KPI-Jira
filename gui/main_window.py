import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import pandas as pd
import os
import webbrowser
from datetime import datetime
import platform
import subprocess
from jira.api import fetch_people_on_project, fetch_issues, fetch_changelog_for_issue, fetch__issues_evolution 
from config.config import TASK_URL

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

        # Cadre pour les filtres (projects, users, start date, end date)
        self.filter_frame_evolution = ttk.LabelFrame(self.tab_evolution, text="Filtres", borderwidth=5, relief="groove", width=100)  
        self.filter_frame_evolution.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Label and dropdown for Projects
        self.project_label = ttk.Label(self.filter_frame_evolution, text="Project:")
        self.project_label.grid(row=0, column=0, padx=5, sticky='w')
        project_names = [project['name'] for project in self.projects]
        self.project_combobox_evol = ttk.Combobox(self.filter_frame_evolution, values=project_names, state="readonly", width=20)
        self.project_combobox_evol.grid(row=0, column=1, padx=5, sticky='w')
        self.project_combobox_evol.bind("<<ComboboxSelected>>", self.update_user_combobox)

        # Label and dropdown for Users
        self.user_label = ttk.Label(self.filter_frame_evolution, text="Users full name:")
        self.user_label.grid(row=0, column=2, padx=5, sticky='w')

        self.user_combobox = ttk.Combobox(self.filter_frame_evolution, state="readonly", width=20)
        self.user_combobox.grid(row=0, column=3, padx=5, sticky='w')

        # Label and DateEntry for Start Date
        self.start_date_label = ttk.Label(self.filter_frame_evolution, text="Start Date:")
        self.start_date_label.grid(row=1, column=0, padx=5, sticky='w')

        self.start_date_entry_evol = DateEntry(self.filter_frame_evolution, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry_evol.grid(row=1, column=1, padx=5, sticky='w')

        # Label and DateEntry for End Date
        self.end_date_label = ttk.Label(self.filter_frame_evolution, text="End Date:")
        self.end_date_label.grid(row=1, column=2, padx=5, sticky='w')

        self.end_date_entry_evol = DateEntry(self.filter_frame_evolution, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry_evol.grid(row=1, column=3, padx=5, sticky='w')

        # Buttons directly under the date fields
        self.input_button_evolution = ttk.Button(self.filter_frame_evolution, text="Refresh Information", command=self.submit_evolution)
        self.input_button_evolution.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        self.export_button_evolution = ttk.Button(self.filter_frame_evolution, text="Export to Excel", command=self.export_results_evolution)
        self.export_button_evolution.grid(row=2, column=2, padx=5, pady=5, sticky='w')


        
        # Cadre principal de l'onglet évolution
        self.main_frame_evolution = ttk.Frame(self.tab_evolution)
        self.main_frame_evolution.pack(expand=True, fill='both', padx=5, pady=5)

        # Cadre de gauche pour les détails Jira
        self.left_frame_evolution = ttk.Frame(self.main_frame_evolution)
        self.left_frame_evolution.pack(side=tk.LEFT, expand=True, fill='both', padx=5, pady=5)

        self.filter_label1 = ttk.Label(self.left_frame_evolution, text="Jira details:")
        self.filter_label1.pack(anchor=tk.W, padx=5, pady=5)

        # Création du Treeview pour afficher les issues
        self.issue_tree1 = ttk.Treeview(self.left_frame_evolution, columns=("ID", "Summary", "Status", "Assignee"),
                                        show='headings')
        self.issue_tree1.heading("ID", text="ID")
        self.issue_tree1.heading("Summary", text="Summary")
        self.issue_tree1.heading("Status", text="Status")
        self.issue_tree1.heading("Assignee", text="Assignee")

        self.issue_tree1.column("ID", width=100)
        self.issue_tree1.column("Summary", width=250)
        self.issue_tree1.column("Status", width=100)
        self.issue_tree1.column("Assignee", width=100)

        self.issue_tree1.pack(expand=True, anchor=tk.W, fill='both', padx=5, pady=5)
        self.issue_tree1.bind("<Double-1>", self.open_jira_task_evolution)
        # Define a tag with a background color for issues without estimation
        self.issue_tree1.tag_configure('no_estimate', background='orange')
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

        self.efficiency_fields = {}
    
        for label in labels:
            ttk.Label(self.right_frame_evolution, text=label).pack(anchor=tk.W, padx=5, pady=5)
            entry = ttk.Entry(self.right_frame_evolution)
            entry.pack(anchor=tk.W, padx=5, pady=5)
            self.efficiency_fields[label] = entry
        
        # L'entrée pour le "Cumulative Estimate (H)"
        self.cumulative_estimate_entry = self.efficiency_fields["Cumulative Estimate (H)"]
        # L'entrée pour le "Cumulative Incurred (H) (Including Tasks Without Estimate)"
        self.cumulative_incurred_entry = self.efficiency_fields["Cumulative Incurred (H) (Including Tasks Without Estimate)"]
        # L'entrée pour le "Cumulative Incurred (H) (Excluding Tasks Without Estimate)"
        self.cumulative_incurred_without_estimate_entry = self.efficiency_fields["Cumulative Incurred (H) (Excluding Tasks Without Estimate)"]
        # L'entrée pour le "Cumulative Efficiency (H)"
        self.cumulative_efficiency_h_entry = self.efficiency_fields["Cumulative Efficiency (H)"]
        # L'entrée pour le "Cumulative Efficiency (%)"
        self.cumulative_efficiency_p_entry = self.efficiency_fields["Cumulative Efficiency (%)"]
        # L'entrée pour le "Number of Efficient Tasks"
        self.efficient_tasks_entry = self.efficiency_fields["Number of Efficient Tasks"]
        # L'entrée pour le "Number of Inefficient Tasks"
        self.inefficient_tasks_entry = self.efficiency_fields["Number of Inefficient Tasks"]
        # L'entrée pour le "Number of Unestimated Tasks"
        self.unestimated_tasks_entry = self.efficiency_fields["Number of Unestimated Tasks"]


    def create_correction_tab(self):
        # Cadre pour les boutons spécifiques à l'onglet "La correction"
        self.button_frame_correction = ttk.Frame(self.tab_correction)
        self.button_frame_correction.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        
        # Cadre pour les filtres de project et dates, avec bordure visible et titre
        # Cadre pour les filtres de project et dates
        self.filter_frame_correction = ttk.LabelFrame(self.tab_correction, text="Filtres", borderwidth=5, relief="groove", width=80)
        self.filter_frame_correction.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Sub-frame for Project Dropdown, Start Date, and End Date (aligned horizontally)
        self.fields_subframe = ttk.Frame(self.filter_frame_correction)
        self.fields_subframe.pack(side=tk.TOP, anchor='w', padx=5, pady=5)

        # Label and dropdown for Projects
        self.project_label = ttk.Label(self.fields_subframe, text="Project:")
        self.project_label.pack(side=tk.LEFT, padx=5, pady=5)

        project_names = [project['name'] for project in self.projects]
        self.project_combobox = ttk.Combobox(self.fields_subframe, values=project_names, state="readonly", width=20)
        self.project_combobox.pack(side=tk.LEFT, padx=5, pady=5)

        # Label and DateEntry for Start Date
        self.start_date_label = ttk.Label(self.fields_subframe, text="Start Date:")
        self.start_date_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.start_date_entry = DateEntry(self.fields_subframe, width=18, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Label and DateEntry for End Date
        self.end_date_label = ttk.Label(self.fields_subframe, text="End Date:")
        self.end_date_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.end_date_entry = DateEntry(self.fields_subframe, width=18, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Sub-frame for buttons (placed below the fields, aligned to the left)
        self.button_frame_correction = ttk.Frame(self.filter_frame_correction)
        self.button_frame_correction.pack(side=tk.TOP, anchor='w', padx=5, pady=10)

        # Input and Export buttons placed under the fields, aligned left
        self.input_button_correction = ttk.Button(self.button_frame_correction, text="Refresh Information", command=self.submit_correction)
        self.input_button_correction.pack(side=tk.LEFT, padx=5)

        self.export_button_correction = ttk.Button(self.button_frame_correction, text="Export to Excel", command=self.export_results_correction)
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

        self.issue_tree.column("ID", width=90)
        self.issue_tree.column("Summary", width=300)
        self.issue_tree.column("Status", width=90)
        self.issue_tree.column("Assignee", width=100)
        self.issue_tree.column("Worklog", width=90)
        self.issue_tree.column("Estimation", width=90)
        self.issue_tree.column("ETC", width=90)
        self.issue_tree.column("Cause", width=300)

        self.issue_tree.pack(expand=True, fill='both', padx=5, pady=5)
        self.issue_tree.bind("<Double-1>", self.open_jira_task_correction)


    """def open_input_window_correction(self):
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
        submit_button_correction.pack(anchor=tk.W, padx=5, pady=5)"""

    """def open_input_window_evolution(self):
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

        submit_button_evolution = ttk.Button(input_window1, text="Submit", command=lambda: self.submit_evolution(input_window1))
        submit_button_evolution.pack(anchor=tk.W, padx=5, pady=5)"""

    def update_user_combobox(self, event):
        # Get the selected project name from the combobox
        project_name = self.project_combobox_evol.get()

        # Check if the projects list contains the selected project
        selected_project = next((project for project in self.projects if project['name'] == project_name), None)

        if selected_project:
            # Get the project key of the selected project
            project_key = selected_project.get('key', None)

            if project_key:
                # Fetch the people assigned to the project
                people = fetch_people_on_project(project_key)

                if people:
                    # Populate the user combobox with the display names of the people
                    user_names = [person['displayName'] for person in people]
                    self.user_combobox['values'] = user_names
                else:
                    messagebox.showerror("Error", "Unable to retrieve people for this project")
            else:
                messagebox.showerror("Error", "Project key not found")
        else:
            # Print project names for debugging purposes
            print("Available projects:", [project['name'] for project in self.projects])
            messagebox.showerror("Error", "Project not found")


    def submit_evolution(self):
        selected_project = self.project_combobox_evol.get()
        selected_user = self.user_combobox.get()
        date_start = self.start_date_entry_evol.get_date()
        date_end = self.end_date_entry_evol.get_date()

        # Clear the Treeview before inserting new data
        for item in self.issue_tree1.get_children():
            self.issue_tree1.delete(item)

        if selected_project and selected_user and date_start and date_end:
            issues = fetch__issues_evolution(selected_project, date_start, date_end, selected_user)
            nombre_taches_efficaces = self.calculer_taches_efficaces(issues)
            nombre_taches_non_efficaces = self.calculer_taches_non_efficaces(issues)
            cumulative_estimate = self.calculer_temps_estime_total(issues)
            cumulative_incurred = self.calculer_temps_total_worklog(issues)
            cumulative_incurred_without_estimate = self.calculer_temps_worklog_sans_estimation(issues)
            cumulative_efficiency_h = round(cumulative_estimate - cumulative_incurred,2)
            if cumulative_incurred != 0:
                cumulative_efficiency_p = round((cumulative_estimate / cumulative_incurred) * 100,2)
            else:
                cumulative_efficiency_p = 0
            unestimated_tasks = self.compter_issues_sans_estimation(issues)

            if issues:
                for issue in issues:
                    print(issue)
                    issuetype = issue.get('issuetype', {})  
                    is_subtask = issuetype.get('subtask', False)
                    issuetype_name = issuetype.get('name', '').lower()

                    if is_subtask or "sub-task" in issuetype_name:
                        original_estimate_seconds = issue.get('timetracking', {}).get('originalEstimateSeconds', None)
                        if original_estimate_seconds is None :
                            self.issue_tree1.insert('', 'end', values=(
                                issue['key'], 
                                issue['summary'], 
                                issue['status'], 
                                issue['assignee']
                            ), tags=('no_estimate',))
                        else:
                            self.issue_tree1.insert('', 'end', values=(
                                issue['key'], 
                                issue['summary'], 
                                issue['status'], 
                                issue['assignee']
                            ))
                    else:
                        sale_estimate = issue.get('sale_estimate', None)  
                        internal_estimate = issue.get('internal_estimate', None) 

                        if (sale_estimate is None or sale_estimate == 0) and (internal_estimate is None or internal_estimate == 0):
                            self.issue_tree1.insert('', 'end', values=(
                                issue['key'], 
                                issue['summary'], 
                                issue['status'], 
                                issue['assignee']
                            ), tags=('no_estimate',))
                        else:
                            self.issue_tree1.insert('', 'end', values=(
                                issue['key'], 
                                issue['summary'], 
                                issue['status'], 
                                issue['assignee']
                            ))
            else:
                tk.messagebox.showinfo("No Issues", "No issues found for the selected criteria.")

            # Mettre à jour le champ "Cumulative Estimate (H)" avec le résultat
            self.cumulative_estimate_entry.delete(0, tk.END)
            self.cumulative_estimate_entry.insert(0, str(cumulative_estimate))

            # Mettre à jour le champ "Cumulative Incurred (H) (Including Tasks Without Estimate)" avec le résultat
            self.cumulative_incurred_entry.delete(0, tk.END)
            self.cumulative_incurred_entry.insert(0, str(cumulative_incurred))

            # Mettre à jour le champ "Number of Efficient Tasks" avec le résultat
            self.efficient_tasks_entry.delete(0, tk.END)
            self.efficient_tasks_entry.insert(0, str(nombre_taches_efficaces))

            # Mettre à jour le champ "Cumulative Efficiency (H)" avec le résultat
            self.cumulative_efficiency_h_entry.delete(0, tk.END)
            self.cumulative_efficiency_h_entry.insert(0, str(cumulative_efficiency_h))

            # Mettre à jour le champ "Cumulative Efficiency (%)" avec le résultat
            self.cumulative_efficiency_p_entry.delete(0, tk.END)
            self.cumulative_efficiency_p_entry.insert(0, str(cumulative_efficiency_p))

            # Mettre à jour le champ "Cumulative Incurred (H) (Excluding Tasks Without Estimate)" avec le résultat
            self.cumulative_incurred_without_estimate_entry.delete(0, tk.END)
            self.cumulative_incurred_without_estimate_entry.insert(0, str(cumulative_incurred_without_estimate))

            # Mettre à jour le champ "Number of Inefficient Tasks" avec le résultat
            self.inefficient_tasks_entry.delete(0, tk.END)
            self.inefficient_tasks_entry.insert(0, str(nombre_taches_non_efficaces))

            # Mettre à jour le champ "Number of Unestimated Tasks" avec le résultat
            self.unestimated_tasks_entry.delete(0, tk.END)
            self.unestimated_tasks_entry.insert(0, str(unestimated_tasks))

        else:
            tk.messagebox.showwarning("Input Error", "Please fill in all fields.")

    def submit_correction(self):
        selected_project = self.project_combobox.get()
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
            print(issue)
            issue_id = issue['key']
            issue_summary = issue['fields']['summary']
            issue_status = issue['fields']['status']['name']
            issue_assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'

            causes = []
            issuetype = issue.get('issuetype', {})  
            is_subtask = issuetype.get('subtask', False)
            issuetype_name = issuetype.get('name', '').lower()
            if is_subtask or "sub-task" in issuetype_name:
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
                if (issue_status == 'Done' or issue_status == 'Delivered') and 'timetracking' in issue['fields'] and 'remainingEstimateSeconds' in issue['fields']['timetracking']:
                    if issue['fields']['timetracking']['remainingEstimateSeconds'] != 0:
                        causes.append("Delivered issue with ETC different from 0")
                
                # Condition 5: Issues dont le statut est différent de done et ETC = 0
                if (issue_status != 'Done' and issue_status != 'Delivered') and 'timetracking' in issue['fields'] and 'remainingEstimateSeconds' in issue['fields']['timetracking']:
                    if issue['fields']['timetracking']['remainingEstimateSeconds'] == 0:
                        causes.append("Undelivered issue with ETC = 0")
                
                # Condition 6: Issues dont plusieurs personnes ont modifié dans le même worklog
                worklog_authors = set()
                if 'worklog' in issue['fields'] and 'worklogs' in issue['fields']['worklog']:
                    worklog_authors.update(entry['author']['displayName'] for entry in issue['fields']['worklog']['worklogs'])
                    
                if len(worklog_authors) > 1:
                    causes.append("Issue with modifications by multiple users")
                    print("Auteurs du worklog :", worklog_authors)
            else:

                # Condition 1: Issues sans estimation
                sale_estimate = issue.get('sale_estimate') or 0 
                if sale_estimate == 0 :
                    causes.append("Issue without estimate")

                # Condition 2: Issues avec un worklog différent de 0 et status open
                parent_logged = issue.get('parent_logged') or 0 
                if issue_status == 'Open' and parent_logged != 0:
                    total_time_spent = sum(entry['timeSpentSeconds'] for entry in issue['fields']['worklog']['worklogs'])
                    if total_time_spent > 0:
                        causes.append("Issue with worklog and status Open")

                # Condition 3: Issues sans worklog et status différent de open
                if issue_status != 'Open' and parent_logged == 0:
                    causes.append("Issue without worklog and status different from Open")
                
                # Condition 4: Issues livrées (statut = Done) avec ETC différent de 0
                parent_remaining = issue.get('aggregatetimeestimate', 0)
                if (issue_status == 'Done' or issue_status == 'Delivered') and parent_remaining != 0:
                    causes.append("Delivered issue with ETC different from 0")
                
                # Condition 5: Issues dont le statut est différent de done et ETC = 0
                if (issue_status != 'Done' and issue_status != 'Delivered') and parent_remaining == 0:
                    causes.append("Undelivered issue with ETC = 0")
                
                
            

            if not causes:
                continue

            # Estimation d'origine
            if 'timetracking' in issue['fields'] and 'originalEstimateSeconds' in issue['fields']['timetracking']:
                total_estimation = issue['fields']['timetracking']['originalEstimateSeconds'] 

                hours, remainder = divmod(total_estimation, 3600)  
                minutes, seconds = divmod(remainder, 60)  
                issue_estimation = f"{hours} h {minutes} min"
            else:
                issue_estimation = 0

            # ETC (estimate to complete)
            if 'timetracking' in issue['fields'] and 'remainingEstimateSeconds' in issue['fields']['timetracking']:
                total_seconds = issue['fields']['timetracking']['remainingEstimateSeconds']
                 
                hours, remainder = divmod(total_seconds, 3600)  
                minutes, seconds = divmod(remainder, 60)  
                issue_etc = f"{hours} h {minutes} min"
                
            else:
                issue_etc = 0 

            # Worklog (temps passé)
            if 'worklog' in issue['fields'] and 'worklogs' in issue['fields']['worklog']:
                total_time = sum(entry['timeSpentSeconds'] for entry in issue['fields']['worklog']['worklogs']) 

                hours, remainder = divmod(total_time, 3600)  
                minutes, seconds = divmod(remainder, 60)  
                total_time_spent = f"{hours} h {minutes} min"
            else:
                total_time_spent = 0

            # Insérer l'issue avec ses détails et les causes spécifiques
            for cause in causes:
                self.issue_tree.insert("", "end", values=(issue_id, issue_summary, issue_status, issue_assignee, total_time_spent, issue_estimation, issue_etc, cause))

        

    def open_jira_task_correction(self, event):
        selected_item = self.issue_tree.selection()

        if selected_item:
            issue_id = self.issue_tree.item(selected_item, 'values')[0]

            jira_link = f"{TASK_URL}/{issue_id}"

            webbrowser.open(jira_link)

    def open_jira_task_evolution(self, event):
        selected_item1 = self.issue_tree1.selection()

        if selected_item1:
            issue_id = self.issue_tree1.item(selected_item1, 'values')[0]

            jira_link = f"{TASK_URL}/{issue_id}"

            webbrowser.open(jira_link)

    def export_results_correction(self):

        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
      
        selected_project = self.combobox_project_var.get()

        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_name = f"jira_results_{selected_project}_{timestamp}.xlsx"
        file_path = os.path.join(downloads_folder, file_name)

        
        data = []
        for i in self.issue_tree.get_children():
            item_values = self.issue_tree.item(i, 'values')
            data.append(item_values)

        df = pd.DataFrame(data,
                        columns=["ID", "Summary", "Status", "Assignee", "Worklog", "Estimation", "ETC", "Cause"])

        
        try:
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            
            tk.messagebox.showinfo("Export Successful", f"Data exported successfully to {file_name}")

            # Open the file automatically after export
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux
                subprocess.call(('xdg-open', file_path))

        except Exception as e:
            tk.messagebox.showwarning("Export Cancelled", f"Failed to export data: {e}")

    
    def export_results_evolution(self):
        # Locate the Downloads folder
        downloads_folder1 = os.path.join(os.path.expanduser("~"), "Downloads")

        date_str1 = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
        file_name1 = f"jira_results_evolution_{date_str1}.xlsx"
        file_path1 = os.path.join(downloads_folder1, file_name1)

        # Prepare data for export
        data = []
        for i in self.issue_tree1.get_children():
            item_values = self.issue_tree1.item(i, 'values')
            data.append(item_values)

        df = pd.DataFrame(data,
                        columns=["ID", "Summary", "Status", "Assignee"])

        # Try exporting the data to the Excel file
        try:
            with pd.ExcelWriter(file_path1, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            
            tk.messagebox.showinfo("Export Successful", f"Data exported successfully to {file_name1}")

            # Open the file automatically after export
            if platform.system() == 'Windows':
                os.startfile(file_path1)
            elif platform.system() == 'Darwin':  
                subprocess.call(('open', file_path1))
            else:  
                subprocess.call(('xdg-open', file_path1))

        except Exception as e:
            tk.messagebox.showwarning("Export Cancelled", f"Failed to export data: {e}")

    def calculer_temps_estime_total(self, issues):
        total_estimated_time = 0  

        for issue in issues:
            issuetype = issue.get('issuetype', {})  
            is_subtask = issuetype.get('subtask', False)
            issuetype_name = issuetype.get('name', '').lower()

            if is_subtask or "sub-task" in issuetype_name:
                original_estimate_seconds = issue.get('timetracking', {}).get('originalEstimateSeconds', 0)
                original_estimate_hours = original_estimate_seconds / 3600
                total_estimated_time += original_estimate_hours
            else:
                # Si parent_estimate_seconds est None, on le remplace par 0
                parent_estimate_seconds = issue.get('parent_estimate') or 0
                parent_estimate_hours = int(parent_estimate_seconds) / 3600  # Conversion en int et division
                total_estimated_time += parent_estimate_hours

        return round(total_estimated_time, 2)

    
    def calculer_temps_total_worklog(self, issues):
        total_worklog_time = 0  

        for issue in issues:
            issuetype = issue.get('issuetype', {})  
            is_subtask = issuetype.get('subtask', False)
            issuetype_name = issuetype.get('name', '').lower()
            if is_subtask or "sub-task" in issuetype_name:
                worklogs = issue.get('worklog', {}).get('worklogs', [])

                for worklog in worklogs:
                    time_spent_seconds = worklog.get('timeSpentSeconds', 0)
                    total_worklog_time += time_spent_seconds
            else:
                parent_logged = issue.get('parent_logged') or 0 
                total_worklog_time += parent_logged

        total_worklog_hours = total_worklog_time / 3600

        return round(total_worklog_hours,2)

    def calculer_temps_worklog_sans_estimation(self, issues):
        total_worklog_time_sans_estimation = 0

        for issue in issues:
            issuetype = issue.get('issuetype', {})  
            is_subtask = issuetype.get('subtask', False)
            issuetype_name = issuetype.get('name', '').lower()
            if is_subtask or "sub-task" in issuetype_name:
                original_estimate_seconds = issue.get('timetracking', {}).get('originalEstimateSeconds', 0) 
                
                if original_estimate_seconds == 0 :
                    worklogs = issue.get('worklog', {}).get('worklogs', [])

                    for worklog in worklogs:
                        time_spent_seconds = worklog.get('timeSpentSeconds', 0)
                        total_worklog_time_sans_estimation += time_spent_seconds
            else:
                parent_logged = issue.get('parent_logged') or 0 
                total_worklog_time_sans_estimation += parent_logged

        total_worklog_hours_sans_estimation = total_worklog_time_sans_estimation / 3600
        return round(total_worklog_hours_sans_estimation,2)

    
    def calculer_taches_efficaces(self, issues):
        nombre_taches_efficaces = 0

        for issue in issues:
            issuetype = issue.get('issuetype', {})  
            is_subtask = issuetype.get('subtask', False)
            issuetype_name = issuetype.get('name', '').lower()

            if is_subtask or "sub-task" in issuetype_name:
                original_estimate_seconds = issue.get('timetracking', {}).get('originalEstimateSeconds', 0)
                worklogs = issue.get('worklog', {}).get('worklogs', [])
                total_time_spent_seconds = sum(entry.get('timeSpentSeconds', 0) for entry in worklogs)

                if total_time_spent_seconds <= original_estimate_seconds:
                    nombre_taches_efficaces += 1
            else:
                sale_estimate = issue.get('sale_estimate') or 0  
                parent_estimate = issue.get('parent_estimate') or 0  
                parent_logged = issue.get('parent_logged') or 0 

                if parent_estimate <= parent_logged:
                    nombre_taches_efficaces += 1
                    
        return nombre_taches_efficaces

    def calculer_taches_non_efficaces(self, issues):
        nombre_taches_non_efficaces = 0

        for issue in issues:
            issuetype = issue.get('issuetype', {})  
            is_subtask = issuetype.get('subtask', False)
            issuetype_name = issuetype.get('name', '').lower()

            if is_subtask or "sub-task" in issuetype_name:
                original_estimate_seconds = issue.get('timetracking', {}).get('originalEstimateSeconds', 0)
                worklogs = issue.get('worklog', {}).get('worklogs', [])
                total_time_spent_seconds = sum(entry.get('timeSpentSeconds', 0) for entry in worklogs)

                if total_time_spent_seconds > original_estimate_seconds:
                    nombre_taches_non_efficaces += 1
            else:
                sale_estimate = issue.get('sale_estimate') or 0  
                parent_estimate = issue.get('parent_estimate') or 0  
                parent_logged = issue.get('parent_logged') or 0 

                if parent_estimate > parent_logged:
                    nombre_taches_non_efficaces += 1
                    
        return nombre_taches_non_efficaces
    
    def compter_issues_sans_estimation(self, issues):
        nombre_issues_sans_estimation = 0

        for issue in issues:
            issuetype = issue.get('issuetype', {})  
            is_subtask = issuetype.get('subtask', False)
            issuetype_name = issuetype.get('name', '').lower()

            if is_subtask or "sub-task" in issuetype_name:
                original_estimate_seconds = issue.get('timetracking', {}).get('originalEstimateSeconds', 0)
                if original_estimate_seconds == 0:
                    nombre_issues_sans_estimation += 1
                    print(f"Issue {issue.get('key')} => Sous-tâche sans estimation détectée.")
            else:
                sale_estimate = issue.get('sale_estimate', None)  
                internal_estimate = issue.get('internal_estimate', None) 

                print(f"Issue {issue.get('key')} - customfield_22631: {sale_estimate}, customfield_22634: {internal_estimate}")

                if (sale_estimate is None or sale_estimate == 0) and (internal_estimate is None or internal_estimate == 0):
                    nombre_issues_sans_estimation += 1
                    print(f"=> Tâche parent sans estimation détectée.")

        print(f"Nombre total d'issues sans estimation : {nombre_issues_sans_estimation}")
        return nombre_issues_sans_estimation









    def run(self):
        self.root.mainloop()
