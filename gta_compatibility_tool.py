import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from pathlib import Path
from collections import defaultdict

class DuplicateFinderApp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("GTA V - COMPATIBILITY TOOL")
        self.root.state('zoomed')
        self.folders_files = {}
        self.dark_mode = tk.BooleanVar(value=True)
        self.ignore_extensions = tk.BooleanVar(value=True)

        self.themes = {
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'drop_bg': '#e6f3ff',
                'drop_border': '#0078d4',
                'text_bg': '#ffffff',
                'text_fg': '#000000'
            },
            'dark': {
                'bg': '#2d2d2d',
                'fg': '#971616',
                'select_bg': "#23443C",
                'select_fg': '#971616',
                'entry_bg': '#404040',
                'entry_fg': '#971616',
                'drop_bg': '#404040',
                'drop_border': '#606060',
                'text_bg': '#1e1e1e',
                'text_fg': "#FFFFFF"
            }
        }
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.style = ttk.Style()
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        toolbar_frame.columnconfigure(1, weight=1)
        
        theme_btn = ttk.Checkbutton(toolbar_frame, text="🌙 Dark mode", 
                                   variable=self.dark_mode, command=self.toggle_theme)
        theme_btn.grid(row=0, column=0, sticky=tk.W)
        
        self.counter_label = ttk.Label(toolbar_frame, text="By Mathdrox | Folders analyzed: 0")
        self.counter_label.grid(row=0, column=2, sticky=tk.E)
        
        instructions = ttk.Label(main_frame, 
                                text="GTA V / FIVEM / SP / RAGE / ALTV - COMPATIBILITY TOOL",
                                font=("Arial", 12))
        instructions.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        filter_frame = ttk.LabelFrame(main_frame, text="🔧 Filter options", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ignore_label = ttk.Label(filter_frame, text="Configure before analysis | Ignore files:")
        ignore_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        extensions_check = ttk.Checkbutton(filter_frame, text=".lua, .txt, .md , .ymt, .xml , .meta, .log, .json, .ini, .cfg, .fxap", 
                                         variable=self.ignore_extensions, 
                                         command=self.update_display)
        extensions_check.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        drop_frame = ttk.Frame(main_frame)
        drop_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        drop_frame.columnconfigure(0, weight=1)
        
        self.drop_label = tk.Label(
            drop_frame,
            text="📁\n\nDrop your folders here\n\n",
            font=("Arial", 26, "bold"),
            height=14,
            relief="solid",
            borderwidth=4,
            cursor="hand2",
            justify="center",
            anchor="center",
            padx=20,
            pady=20,
        )
        self.drop_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=10)
        
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        
        def open_folder_dialog(event=None):
            from tkinter import filedialog
            folder = filedialog.askdirectory(title="Choose a folder to analyze")
            if folder:
                self.on_drop(type("Event", (object,), {"data": folder})())
        
        self.drop_label.bind("<Button-1>", open_folder_dialog)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.files_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.files_frame, text="📋 File list")
        self.files_text = scrolledtext.ScrolledText(self.files_frame, height=20, width=80,
                                                   wrap=tk.WORD, font=("Consolas", 10),
                                                   state='disabled')
        self.files_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.duplicates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.duplicates_frame, text="🔍 Duplicates detected")
        self.duplicates_text = scrolledtext.ScrolledText(self.duplicates_frame, height=20, width=80,
                                                        wrap=tk.WORD, font=("Consolas", 10),
                                                        state='disabled')
        self.duplicates_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 Statistics")
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, height=20, width=80,
                                                   wrap=tk.WORD, font=("Consolas", 10),
                                                   state='disabled')
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear all", command=self.clear_all)
        clear_btn.grid(row=0, column=0, sticky=tk.W)
        
        export_btn = ttk.Button(buttons_frame, text="💾 Export results", command=self.export_results)
        export_btn.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        delete_btn = ttk.Button(buttons_frame, text="❌ Delete duplicates...", command=self.delete_duplicates_dialog)
        delete_btn.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))

    def delete_duplicates_dialog(self):
        duplicates = self.find_duplicates()
        if not duplicates:
            messagebox.showinfo("Info", "No duplicates to delete.")
            return
        
        folders = list(self.folders_files.keys())
        if not folders:
            messagebox.showinfo("Info", "No folder loaded.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete duplicates in a folder")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        label = ttk.Label(dialog, text="Choose the folder where to delete duplicates:")
        label.pack(pady=10)
        
        folder_var = tk.StringVar(value=folders[0])
        folder_menu = ttk.Combobox(dialog, textvariable=folder_var, values=folders, state="readonly")
        folder_menu.pack(pady=10)
        
        def on_confirm():
            selected_folder = folder_var.get()
            self.delete_duplicates_in_folder(selected_folder)
            dialog.destroy()
        
        confirm_btn = ttk.Button(dialog, text="Delete duplicates", command=on_confirm)
        confirm_btn.pack(pady=10)
        
        cancel_btn = ttk.Button(dialog, text="Cancel", command=dialog.destroy)
        cancel_btn.pack()

    def delete_duplicates_in_folder(self, folder_name):
        duplicates = self.find_duplicates()
        if not duplicates or folder_name not in self.folders_files:
            messagebox.showinfo("Info", "No duplicates to delete in this folder.")
            return
        
        files_to_delete = []
        for filename, locations in duplicates.items():
            for loc in locations[1:]:
                if loc['folder'] == folder_name:
                    files_to_delete.append(loc['path'])
        
        if not files_to_delete:
            messagebox.showwarning("Warning", f"No duplicates to delete in the folder, no duplicate is in this folder '{folder_name}'.")
            return
        
        if not messagebox.askyesno("Confirmation", f"Delete {len(files_to_delete)} duplicate(s) in '{folder_name}'?\nThis action is irreversible."):
            return
        
        deleted = 0
        errors = []
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted += 1
            except Exception as e:
                errors.append(f"{file_path}: {e}")
        
        # Réanalyse le dossier même si certains fichiers n'ont pas pu être supprimés
        self.analyze_folder(self.folders_files[folder_name]['path'])
        self.update_display()
        
        msg = f"{deleted} duplicate(s) deleted in '{folder_name}'."
        if errors:
            msg += f"\n\nImpossible de supprimer {len(errors)} fichier(s) :\n" + "\n".join(errors)
        messagebox.showinfo("Suppression terminée", msg)

    def should_ignore_file(self, filename):
        if not self.ignore_extensions.get():
            return False
        ext = Path(filename).suffix.lower()
        return ext in ['.lua', '.txt', '.md', '.ymt', '.xml', '.meta', '.log', '.json', '.ini', '.cfg', '.fxap']
        
    def get_files_from_folder(self, folder_path):
        files = []
        try:
            folder = Path(folder_path)
            if folder.is_dir():
                for file_path in folder.rglob('*'):
                    if file_path.is_file() and not self.should_ignore_file(file_path.name):
                        files.append(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading folder {folder_path}: {e}")
        return files
        
    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        new_folders = 0
        for file_path in files:
            if os.path.isdir(file_path):
                folder_name = os.path.basename(file_path)
                if folder_name not in self.folders_files:
                    self.analyze_folder(file_path)
                    new_folders += 1
                else:
                    messagebox.showinfo("Information", f"The folder '{folder_name}' is already analyzed.")
        if new_folders > 0:
            self.update_display()
            messagebox.showinfo("Success", f"{new_folders} new folder(s) analyzed!")
        
    def analyze_folder(self, folder_path):
        folder_name = os.path.basename(folder_path)
        files = self.get_files_from_folder(folder_path)
        file_names = []
        for file_path in files:
            try:
                file_names.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size if file_path.exists() else 0,
                    'extension': file_path.suffix.lower()
                })
            except Exception as e:
                print(f"Error with file {file_path}: {e}")
        
        self.folders_files[folder_name] = {
            'path': folder_path,
            'files': file_names
        }
        
    def find_duplicates(self):
        if len(self.folders_files) < 2:
            return {}
        
        file_locations = defaultdict(list)
        for folder_name, folder_data in self.folders_files.items():
            for file_info in folder_data['files']:
                if not self.should_ignore_file(file_info['name']):
                    file_locations[file_info['name']].append({
                        'folder': folder_name,
                        'path': file_info['path'],
                        'size': file_info['size'],
                        'extension': file_info['extension']
                    })
        
        duplicates = {}
        for filename, locations in file_locations.items():
            if len(locations) > 1:
                duplicates[filename] = locations
        
        return duplicates
        
    def get_statistics(self):
        stats = {
            'total_folders': len(self.folders_files),
            'total_files': 0,
            'total_size': 0,
            'extensions': defaultdict(int),
            'duplicates_count': 0,
            'duplicates_size': 0
        }
        
        for folder_data in self.folders_files.values():
            for file_info in folder_data['files']:
                if not self.should_ignore_file(file_info['name']):
                    stats['total_files'] += 1
                    stats['total_size'] += file_info['size']
                    stats['extensions'][file_info['extension']] += 1
        
        duplicates = self.find_duplicates()
        stats['duplicates_count'] = len(duplicates)
        for filename, locations in duplicates.items():
            file_size = locations[0]['size']
            stats['duplicates_size'] += file_size * (len(locations) - 1)
        
        return stats
        
    def update_text_widget(self, widget, content):
        widget.config(state='normal')
        widget.delete(1.0, tk.END)
        widget.insert(1.0, content)
        widget.config(state='disabled')
        
    def update_display(self):
        files_content = ""
        for folder_name, folder_data in self.folders_files.items():
            filtered_files = [f for f in folder_data['files'] if not self.should_ignore_file(f['name'])]
            files_content += f"📁 FOLDER: {folder_name}\n"
            files_content += f"   Path: {folder_data['path']}\n"
            files_content += f"   Number of files: {len(filtered_files)}\n\n"
            for file_info in filtered_files:
                size_mb = file_info['size'] / (1024 * 1024)
                files_content += f"   📄 {file_info['name']} ({size_mb:.2f} MB)\n"
            files_content += "\n" + "="*80 + "\n\n"
        
        self.update_text_widget(self.files_text, files_content)
        
        duplicates_content = ""
        duplicates = self.find_duplicates()
        if duplicates:
            duplicates_content += f"🔍 DUPLICATES DETECTED ({len(duplicates)} files)\n\n"
            for filename, locations in duplicates.items():
                duplicates_content += f"📄 {filename}\n"
                duplicates_content += f"   Found in {len(locations)} folders:\n"
                for i, location in enumerate(locations):
                    size_mb = location['size'] / (1024 * 1024)
                    icon = "🔴" if i > 0 else "✅"
                    duplicates_content += f"   {icon} {location['folder']} ({size_mb:.2f} MB)\n"
                    duplicates_content += f"      {location['path']}\n"
                duplicates_content += "\n"
        else:
            if len(self.folders_files) >= 2:
                duplicates_content += "✅ No duplicates detected between folders!\n"
            else:
                duplicates_content += "ℹ️ Drag at least 2 folders to detect duplicates.\n"
        
        self.update_text_widget(self.duplicates_text, duplicates_content)
        
        stats_content = ""
        stats = self.get_statistics()
        stats_content += "📊 DETAILED STATISTICS\n\n"
        stats_content += f"📁 Folders analyzed: {stats['total_folders']}\n"
        stats_content += f"📄 Total files: {stats['total_files']}\n"
        stats_content += f"💾 Total size: {stats['total_size'] / (1024**2):.2f} MB\n"
        stats_content += f"🔍 Duplicates found: {stats['duplicates_count']}\n"
        stats_content += f"💸 Space wasted by duplicates: {stats['duplicates_size'] / (1024**2):.2f} MB\n\n"
        stats_content += "📈 Create for Mathdrox\n"
        for ext, count in sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True):
            ext_name = ext if ext else "(no extension)"
            stats_content += f"   {ext_name}: {count} files\n"
        
        self.update_text_widget(self.stats_text, stats_content)
        
        self.counter_label.configure(text=f"By Mathdrox | Folders analyzed: {len(self.folders_files)}")
        
    def toggle_theme(self):
        self.apply_theme()
        
    def apply_theme(self):
        theme = self.themes['dark'] if self.dark_mode.get() else self.themes['light']
        
        self.root.configure(bg=theme['bg'])
        
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=theme['bg'])
            except Exception:
                pass
        
        self.drop_label.configure(
            bg=theme['drop_bg'],
            fg=theme['fg'],
            highlightbackground=theme['drop_border'],
            highlightcolor=theme['drop_border'],
            highlightthickness=2,
            activebackground=theme['drop_bg'],
            activeforeground=theme['fg'],
        )
        
        for text_widget in [self.files_text, self.duplicates_text, self.stats_text]:
            text_widget.configure(
                bg=theme['text_bg'],
                fg=theme['text_fg'],
                insertbackground=theme['fg'],
                selectbackground=theme['select_bg'],
                selectforeground=theme['select_fg'],
                highlightbackground=theme['drop_border'],
                highlightcolor=theme['drop_border'],
                borderwidth=1,
                relief="solid"
            )
        
        if self.dark_mode.get():
            self.style.theme_use('clam')
            dark_widgets = [
                'TLabel', 'TFrame', 'TLabelFrame', 'TCheckbutton', 'TButton', 'TNotebook', 'TNotebook.Tab', 'TCombobox'
            ]
            for widget_style in dark_widgets:
                self.style.configure(widget_style, background=theme['bg'], foreground=theme['fg'])
            
            self.style.configure('TEntry', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])
            self.style.map('TNotebook.Tab',
                background=[('selected', theme['drop_bg']), ('!selected', theme['bg'])],
                foreground=[('selected', theme['fg']), ('!selected', theme['fg'])]
            )
            
            self.style.configure('TNotebook', background=theme['bg'], borderwidth=0)
            self.style.configure('TNotebook.Tab', background=theme['bg'], foreground=theme['fg'])
            self.style.configure('TLabelFrame', background=theme['bg'], foreground=theme['fg'])
            self.style.configure('TCombobox', fieldbackground=theme['entry_bg'], background=theme['entry_bg'], foreground=theme['entry_fg'])
        else:
            self.style.theme_use('default')
        
        for frame in self.root.winfo_children():
            if isinstance(frame, (ttk.Frame, ttk.LabelFrame)):
                try:
                    frame.configure(style='TFrame')
                except Exception:
                    pass
            for child in frame.winfo_children():
                if isinstance(child, (ttk.Frame, ttk.LabelFrame)):
                    try:
                        child.configure(style='TFrame')
                    except Exception:
                        pass

    def export_results(self):
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export results"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=== DUPLICATE ANALYSIS REPORT ===\n\n")
                    
                    stats = self.get_statistics()
                    f.write("STATISTICS:\n")
                    f.write(f"- Folders analyzed: {stats['total_folders']}\n")
                    f.write(f"- Total files: {stats['total_files']}\n")
                    f.write(f"- Duplicates found: {stats['duplicates_count']}\n\n")
                    
                    duplicates = self.find_duplicates()
                    f.write("DETECTED DUPLICATES:\n")
                    for filename, locations in duplicates.items():
                        f.write(f"\n• {filename}\n")
                        for location in locations:
                            f.write(f"  - {location['folder']}: {location['path']}\n")
                
                messagebox.showinfo("Success", f"Results exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error during export: {e}")
        
    def clear_all(self):
        self.folders_files.clear()
        self.counter_label.configure(text="By Mathdrox | Folders analyzed: 0")
        
        self.update_text_widget(self.files_text, "Drag and drop folders to start analysis...\n")
        self.update_text_widget(self.duplicates_text, "ℹ️ Drag at least 2 folders to detect duplicates.\n")
        self.update_text_widget(self.stats_text, "📊 Statistics will appear here after folder analysis.\n")
        
    def run(self):
        self.clear_all()
        self.root.mainloop()

if __name__ == "__main__":
    app = DuplicateFinderApp()
    app.run()