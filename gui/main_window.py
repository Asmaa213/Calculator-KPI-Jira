import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import pandas as pd
import os
from jira.api import fetch_people_on_project 

class MainWindow:
    def __init__(self, projects):
        self.root = tk.Tk()
        self.root.title("Jira Data Extractor")
        self.projects = projects  # Store the projects
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

        self.input_button_evolution = ttk.Button(self.button_frame_evolution, text="Actualiser information", command=self.open_input_window_evolution)
        self.input_button_evolution.pack(side=tk.LEFT, padx=5)

        self.export_button_evolution = ttk.Button(self.button_frame_evolution, text="Exporter à Excel", command=self.export_results)
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
        ttk.Label(self.right_frame_evolution, text="EFFICIENCE").pack(anchor=tk.W, padx=5, pady=5)

        labels = [
            "Estimation accumulée (H)",
            "Incurré accumulé (H)\n(Incluant les tâches sans estimation)",
            "Incurré accumulé (H)\n(Excluant les tâches sans estimation)",
            "Efficacité accumulée (H)",
            "Efficacité accumulée (%)",
            "Nombre de tâches efficaces",
            "Nombre de tâches inefficaces",
            "Nombre de tâches non estimées"
        ]

        for label in labels:
            ttk.Label(self.right_frame_evolution, text=label).pack(anchor=tk.W, padx=5, pady=5)
            ttk.Entry(self.right_frame_evolution).pack(anchor=tk.W, padx=5, pady=5)

    def create_correction_tab(self):
        # Cadre pour les boutons spécifiques à l'onglet "La correction"
        self.button_frame_correction = ttk.Frame(self.tab_correction)
        self.button_frame_correction.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.input_button_correction = ttk.Button(self.button_frame_correction, text="Actualiser information", command=self.open_input_window_correction)
        self.input_button_correction.pack(side=tk.LEFT, padx=5)

        self.export_button_correction = ttk.Button(self.button_frame_correction, text="Exporter à Excel", command=self.export_results)
        self.export_button_correction.pack(side=tk.LEFT, padx=5)

        # Cadre principal de l'onglet correction
        self.main_frame_correction = ttk.Frame(self.tab_correction)
        self.main_frame_correction.pack(expand=True, fill='both', padx=5, pady=5)

        # Cadre de gauche pour les détails Jira
        self.left_frame_correction = ttk.Frame(self.main_frame_correction)
        self.left_frame_correction.pack(side=tk.LEFT, expand=True, fill='both', padx=5, pady=5)

        self.filter_label2 = ttk.Label(self.left_frame_correction, text="Jira errors:")
        self.filter_label2.pack(anchor=tk.W, padx=5, pady=5)

        self.result_text2 = tk.Text(self.left_frame_correction, height=20, width=80)
        self.result_text2.pack(anchor=tk.W, padx=5, pady=5, expand=True, fill=tk.BOTH)

    def open_input_window_correction(self):
        # Logique pour ouvrir une nouvelle fenêtre d'entrée des informations
        input_window = tk.Toplevel(self.root)
        input_window.title("Entrer les informations")

        # Cadre pour les combobox
        combobox_frame = ttk.Frame(input_window)
        combobox_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        # Combobox pour les projets
        combobox_label2 = ttk.Label(combobox_frame, text="Projets:")
        combobox_label2.pack(side=tk.LEFT, padx=5, pady=5)

        project_names = [project['name'] for project in self.projects]
        combobox2 = ttk.Combobox(combobox_frame, values=project_names, state='readonly')
        combobox2.pack(side=tk.LEFT, padx=5, pady=5)

        # Cadre pour les dates
        date_frame = ttk.Frame(input_window)
        date_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        date_label_start = ttk.Label(date_frame, text="Start Date:")
        date_label_start.pack(side=tk.LEFT, padx=5, pady=5)

        date_start = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_start.pack(side=tk.LEFT, padx=5, pady=5)

        date_label_end = ttk.Label(date_frame, text="End Date:")
        date_label_end.pack(side=tk.LEFT, padx=5, pady=5)

        date_end = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_end.pack(side=tk.LEFT, padx=5, pady=5)

        submit_button_correction = ttk.Button(input_window, text="Submit", command=self.submit_correction)
        submit_button_correction.pack(anchor=tk.W, padx=5, pady=5)

    def open_input_window_evolution(self):
        # Logique pour ouvrir une nouvelle fenêtre d'entrée des informations
        input_window1 = tk.Toplevel(self.root)
        input_window1.title("Entrer les informations")

        # Cadre pour les combobox
        combobox_frame = ttk.Frame(input_window1)
        combobox_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        # Combobox pour les projets
        combobox_label2 = ttk.Label(combobox_frame, text="Projets:")
        combobox_label2.pack(side=tk.LEFT, padx=5, pady=5)

        project_names = [project['name'] for project in self.projects]
        self.combobox2 = ttk.Combobox(combobox_frame, values=project_names, state='readonly')
        self.combobox2.pack(side=tk.LEFT, padx=5, pady=5)
        self.combobox2.bind("<<ComboboxSelected>>", self.update_user_combobox)  # Ajouter la liaison de l'événement de sélection

        # Combobox pour le nom d'utilisateur
        combobox_label = ttk.Label(combobox_frame, text="User's full name:")
        combobox_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.combobox = ttk.Combobox(combobox_frame, state='readonly')  # Ne pas définir les valeurs ici
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
                # Mettre à jour les options de la combobox des utilisateurs
                user_names = [person['displayName'] for person in people]
                self.combobox['values'] = user_names
                self.combobox.set('')  # Effacer la sélection précédente
            else:
                messagebox.showerror("Erreur", "Impossible de récupérer les personnes sur ce projet")
        else:
            messagebox.showerror("Erreur", "Projet non trouvé")

    def submit_evolution(self):
        # Logique pour le bouton "Submit" de l'onglet "L'evolution"
        selected_user = self.combobox.get()
        start_date = self.date_start.get()
        end_date = self.date_end.get()

        # Vous pouvez utiliser les valeurs sélectionnées pour effectuer d'autres actions, par exemple, interroger Jira

        messagebox.showinfo("Submit", "Evolution submitted")


    def submit_correction(self):
        # Logique pour le bouton "Submit" de l'onglet "La correction"
        messagebox.showinfo("Submit", "Correction submitted")


    def export_results(self):
        # Logique pour exporter les résultats
        data = [
            {'summary': 'Issue 1', 'status': 'Open', 'assignee': 'User A'},
            {'summary': 'Issue 2', 'status': 'In Progress', 'assignee': 'User B'}
        ]
        df = pd.DataFrame(data)
        file_path = os.path.join(os.path.expanduser("~"), "jira_results.xlsx")
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Export", f"Résultats exportés avec succès vers {file_path}")

    def run(self):
        self.root.mainloop()
