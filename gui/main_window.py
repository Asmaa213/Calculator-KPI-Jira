import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
#from jira.api import fetch_jira_data

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jira Data Extractor")
        self.create_widgets()

    def create_widgets(self):
        # Créer un widget Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Créer les cadres pour les onglets
        self.tab_evolution = ttk.Frame(self.notebook)
        self.tab_correction = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_evolution, text="L'évolution")
        self.notebook.add(self.tab_correction, text="La correction")

        # Ajouter du contenu à l'onglet "L'évolution"
        self.create_evolution_tab()

        # Ajouter du contenu à l'onglet "La correction"
        self.create_correction_tab()

    def create_evolution_tab(self):
        # Widgets spécifiques à l'onglet "L'évolution"
        self.filter_label1 = ttk.Label(self.tab_evolution, text="Filtre JQL:")
        self.filter_label1.grid(row=0, column=0, sticky=tk.W)

        self.filter_entry1 = ttk.Entry(self.tab_evolution, width=50)
        self.filter_entry1.grid(row=0, column=1, sticky=(tk.W, tk.E))

        self.search_button1 = ttk.Button(self.tab_evolution, text="Rechercher", command=self.search_evolution)
        self.search_button1.grid(row=0, column=2, sticky=tk.E)

        self.result_text1 = tk.Text(self.tab_evolution, height=20, width=80)
        self.result_text1.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))

    def create_correction_tab(self):
        # Widgets spécifiques à l'onglet "La correction"
        

        self.combobox_label2 = ttk.Label(self.tab_correction, text="Projets:")
        self.combobox_label2.grid(row=1, column=0, sticky=tk.W)

        self.options2 = ['Projet X', 'Projet Y', 'Projet Z']
        self.combobox2 = ttk.Combobox(self.tab_correction, values=self.options2, state='readonly')
        self.combobox2.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))

        self.date_label_start = ttk.Label(self.tab_correction, text="Start Date:")
        self.date_label_start.grid(row=2, column=0, sticky=tk.W)

        self.date_start = DateEntry(self.tab_correction, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.date_start.grid(row=2, column=1, sticky=tk.W)

        self.date_label_end = ttk.Label(self.tab_correction, text="End Date:")
        self.date_label_end.grid(row=2, column=2, sticky=tk.W)

        self.date_end = DateEntry(self.tab_correction, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_end.grid(row=2, column=3, sticky=tk.W)

        self.submit_button = ttk.Button(self.tab_correction, text="Submit", command=self.submit_correction)
        self.submit_button.grid(row=3, column=1, columnspan=3, padx=10, sticky=tk.W)


    def search_evolution(self):
        # Logique pour l'onglet "L'évolution"
        jql = self.filter_entry1.get()
        data = fetch_jira_data(jql)
        self.display_results(data, self.result_text1)

    def search_correction(self):
        # Logique pour l'onglet "La correction"
        jql = self.filter_entry2.get()
        data = fetch_jira_data(jql)
        self.display_results(data, self.result_text2)

    def submit_correction(self):
        # Logique pour le bouton "Submit" de l'onglet "La correction"
        messagebox.showinfo("Submit", "Données soumises avec succès!")


    def display_results(self, data, text_widget):
        text_widget.delete('1.0', tk.END)
        for issue in data:
            summary = issue['fields']['summary']
            status = issue['fields']['status']['name']
            assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else "Unassigned"
            text_widget.insert(tk.END, f"Summary: {summary}\nStatus: {status}\nAssignee: {assignee}\n\n")

    def run(self):
        self.root.mainloop()
