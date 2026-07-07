# edu_launcher_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from minecraft_edu_launcher import MinecraftEduLauncher
import json
import threading
import os
import webbrowser
import shutil

class EduLauncherGUI:
    def __init__(self):
        self.launcher = MinecraftEduLauncher()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Minecraft Education Launcher")
        self.root.geometry("900x550")
        
        self.setup_ui()
        self.show_worlds()
        
    def setup_ui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Logo/Title
        self.title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Minecraft\nEducation Edition", 
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=20)
        
        # Quick Launch button
        self.quick_launch_btn = ctk.CTkButton(
            self.sidebar,
            text="▶ Launch Game",
            command=self.quick_launch,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color="green",
            hover_color="dark green"
        )
        self.quick_launch_btn.pack(fill="x", padx=10, pady=(0, 20))
        
        # Navigation buttons
        nav_items = [
            ("🌍 Worlds", self.show_worlds),
            ("🧩 Addons", self.show_addons),
            ("💾 Backups", self.show_backups),
            ("⚙️ Settings", self.show_settings),
        ]
        
        for text, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                anchor="w",
                height=35
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Status info at bottom of sidebar
        edu_path = self.launcher.config.get("edu_exe_path") or self.launcher.edu_exe_path
        if edu_path and os.path.exists(edu_path):
            status_text = "✅ Game Found"
            status_color = "green"
        else:
            status_text = "❌ Game Not Found"
            status_color = "red"
        
        self.status_indicator = ctk.CTkLabel(
            self.sidebar,
            text=status_text,
            font=("Arial", 10),
            text_color=status_color
        )
        self.status_indicator.pack(side="bottom", pady=10)
        
        # Content area
        self.content = ctk.CTkFrame(self.main_container)
        self.content.pack(side="right", fill="both", expand=True)
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self.root,
            text="Ready",
            anchor="w",
            height=25
        )
        self.status_bar.pack(side="bottom", fill="x")
    
    def quick_launch(self):
        """Quick launch Minecraft Education Edition"""
        try:
            self.status_bar.configure(text="Launching Minecraft Education Edition...")
            self.quick_launch_btn.configure(state="disabled", text="Launching...")
            
            def launch():
                try:
                    success = self.launcher.launch_education_edition()
                    if success:
                        self.root.after(0, lambda: self.status_bar.configure(
                            text="Minecraft is running!"
                        ))
                    self.root.after(0, lambda: self.quick_launch_btn.configure(
                        state="normal", text="▶ Launch Game"
                    ))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Launch Error", str(e)))
                    self.root.after(0, lambda: self.status_bar.configure(text="Ready"))
                    self.root.after(0, lambda: self.quick_launch_btn.configure(
                        state="normal", text="▶ Launch Game"
                    ))
            
            threading.Thread(target=launch, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.quick_launch_btn.configure(state="normal", text="▶ Launch Game")
    
    def show_worlds(self):
        """Display worlds view"""
        self.clear_content()
        
        # Header
        header = ctk.CTkFrame(self.content)
        header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            header,
            text="Your Worlds",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)
        
        btn_frame = ctk.CTkFrame(header)
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="📁 Open Folder",
            command=self.open_worlds_folder,
            width=110
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            command=self.show_worlds,
            width=80
        ).pack(side="left", padx=5)
        
        # Worlds list
        self.worlds_frame = ctk.CTkScrollableFrame(self.content)
        self.worlds_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        worlds = self.launcher.get_worlds()
        
        if not worlds:
            empty_frame = ctk.CTkFrame(self.worlds_frame)
            empty_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(
                empty_frame,
                text="No worlds found!\n\n"
                     "Create a world in Minecraft Education Edition first.\n"
                     "Then click Refresh to see it here.",
                font=("Arial", 14)
            ).pack(pady=50)
            return
        
        for world in worlds:
            self.create_world_card(world)
    
    def create_world_card(self, world):
        """Create a world card widget"""
        card = ctk.CTkFrame(self.worlds_frame)
        card.pack(fill="x", padx=5, pady=5)
        
        # World icon
        icon_label = ctk.CTkLabel(
            card,
            text="🌍",
            font=("Arial", 30)
        )
        icon_label.pack(side="left", padx=10, pady=10)
        
        # World info
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=world["name"],
            font=("Arial", 14, "bold")
        ).pack(anchor="w")
        
        details = f"Size: {world['size_mb']} MB"
        if world.get("last_played"):
            try:
                last_played = world["last_played"][:10]
                details += f" | Last played: {last_played}"
            except:
                pass
        
        ctk.CTkLabel(
            info_frame,
            text=details,
            font=("Arial", 10),
            text_color="gray"
        ).pack(anchor="w")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card)
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="📂 Open",
            command=lambda w=world: self.launcher.open_world_folder(w["path"]),
            width=70,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Backup",
            command=lambda w=world: self.backup_world(w),
            width=80,
            height=30,
            fg_color="blue"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            command=lambda w=world: self.delete_world(w),
            width=70,
            height=30,
            fg_color="red"
        ).pack(side="left", padx=5)
    
    def delete_world(self, world):
        """Delete a world"""
        if messagebox.askyesno("Delete World", 
            f"Are you sure you want to delete '{world['name']}'?\n\n"
            "This cannot be undone! Make a backup first."):
            try:
                shutil.rmtree(world["path"])
                messagebox.showinfo("Deleted", f"World '{world['name']}' deleted!")
                self.show_worlds()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete world: {str(e)}")
    
    def show_addons(self):
        """Show addons management view"""
        self.clear_content()
        
        # Header
        header = ctk.CTkFrame(self.content)
        header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            header,
            text="Addons",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)
        
        btn_frame = ctk.CTkFrame(header)
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="📁 Open Addons Folder",
            command=self.open_addons_folder,
            width=140
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            command=self.show_addons,
            width=80
        ).pack(side="left", padx=5)
        
        # Browse addons online button
        browse_frame = ctk.CTkFrame(self.content)
        browse_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            browse_frame,
            text="Find more addons online:",
            font=("Arial", 12)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            browse_frame,
            text="🔍 Browse CurseForge Addons",
            command=self.open_curseforge,
            height=35,
            fg_color="#f16436",
            hover_color="#d44d26"
        ).pack(side="left", padx=10)
        
        # Addons list
        self.addons_frame = ctk.CTkScrollableFrame(self.content)
        self.addons_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        addons = self.launcher.get_addons()
        
        if not addons:
            empty_frame = ctk.CTkFrame(self.addons_frame)
            empty_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(
                empty_frame,
                text="No addons installed!\n\n"
                     "Click 'Browse CurseForge Addons' to find addons.\n"
                     "Download .mcaddon or .mcpack files and place them in the addons folder.",
                font=("Arial", 14)
            ).pack(pady=30)
            
            ctk.CTkButton(
                empty_frame,
                text="🔍 Browse CurseForge Addons",
                command=self.open_curseforge,
                fg_color="#f16436",
                hover_color="#d44d26"
            ).pack(pady=10)
            return
        
        for addon in addons:
            self.create_addon_card(addon)
    
    def create_addon_card(self, addon):
        """Create an addon card widget"""
        card = ctk.CTkFrame(self.addons_frame)
        card.pack(fill="x", padx=5, pady=5)
        
        # Addon icon
        icon_label = ctk.CTkLabel(
            card,
            text="🧩",
            font=("Arial", 30)
        )
        icon_label.pack(side="left", padx=10, pady=10)
        
        # Addon info
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=addon["name"],
            font=("Arial", 14, "bold")
        ).pack(anchor="w")
        
        # Addon type
        addon_type = addon.get("type", "Unknown")
        type_colors = {
            "resource_pack": "📦 Resource Pack",
            "behavior_pack": "⚙️ Behavior Pack",
            "skin_pack": "👤 Skin Pack",
            "world_template": "🌍 World Template",
            "addon": "🧩 Addon"
        }
        type_text = type_colors.get(addon_type, f"📄 {addon_type}")
        
        ctk.CTkLabel(
            info_frame,
            text=type_text,
            font=("Arial", 10),
            text_color="gray"
        ).pack(anchor="w")
        
        if addon.get("size_mb"):
            ctk.CTkLabel(
                info_frame,
                text=f"Size: {addon['size_mb']} MB",
                font=("Arial", 10),
                text_color="gray"
            ).pack(anchor="w")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card)
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="📂 Open",
            command=lambda a=addon: self.launcher.open_addon_folder(a["path"]),
            width=70,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            command=lambda a=addon: self.delete_addon(a),
            width=70,
            height=30,
            fg_color="red"
        ).pack(side="left", padx=5)
    
    def delete_addon(self, addon):
        """Delete an addon"""
        if messagebox.askyesno("Delete Addon", 
            f"Are you sure you want to delete '{addon['name']}'?"):
            try:
                if os.path.isfile(addon["path"]):
                    os.remove(addon["path"])
                elif os.path.isdir(addon["path"]):
                    shutil.rmtree(addon["path"])
                messagebox.showinfo("Deleted", f"Addon '{addon['name']}' deleted!")
                self.show_addons()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete addon: {str(e)}")
    
    def open_addons_folder(self):
        """Open the addons folder"""
        addons_path = self.launcher.get_addons_path()
        if addons_path and os.path.exists(addons_path):
            os.startfile(addons_path)
        else:
            messagebox.showwarning("Not Found", 
                "Addons folder not found.\n\n"
                "It will be created when you first install an addon.")
    
    def open_curseforge(self):
        """Open CurseForge addons page"""
        url = "https://www.curseforge.com/minecraft-bedrock/search?class=addons&page=1&pageSize=20&sortBy=relevancy"
        webbrowser.open(url)
        self.status_bar.configure(text="Opened CurseForge in browser - download .mcaddon files to install")
    
    def backup_world(self, world):
        """Backup a world"""
        try:
            backup_path = self.launcher.backup_world(world["path"])
            messagebox.showinfo("Backup Created", 
                f"World backed up successfully!\n\nSaved to:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Backup Error", str(e))
    
    def open_worlds_folder(self):
        """Open the worlds folder"""
        worlds_path = self.launcher.config.get("worlds_path") or self.launcher.worlds_path
        if worlds_path and os.path.exists(worlds_path):
            os.startfile(worlds_path)
        else:
            messagebox.showwarning("Not Found", 
                "Worlds folder not found.\n\n"
                "Please check Settings and set the correct worlds path.")
    
    def show_backups(self):
        """Show backups view"""
        self.clear_content()
        
        ctk.CTkLabel(
            self.content,
            text="Backups",
            font=("Arial", 18, "bold")
        ).pack(pady=20)
        
        backups_dir = self.launcher.base_dir / "backups"
        
        if not backups_dir.exists() or not any(backups_dir.iterdir()):
            ctk.CTkLabel(
                self.content,
                text="No backups yet.\n\nBackup your worlds to see them here.",
                font=("Arial", 14)
            ).pack(pady=50)
        else:
            backup_list = ctk.CTkScrollableFrame(self.content)
            backup_list.pack(fill="both", expand=True, padx=20, pady=10)
            
            for backup_file in sorted(backups_dir.iterdir(), reverse=True):
                if backup_file.is_file():
                    backup_card = ctk.CTkFrame(backup_list)
                    backup_card.pack(fill="x", pady=5)
                    
                    ctk.CTkLabel(
                        backup_card,
                        text=f"📦 {backup_file.name}",
                        font=("Arial", 12)
                    ).pack(side="left", padx=10, pady=10)
                    
                    size_mb = round(backup_file.stat().st_size / (1024 * 1024), 2)
                    ctk.CTkLabel(
                        backup_card,
                        text=f"{size_mb} MB",
                        font=("Arial", 10),
                        text_color="gray"
                    ).pack(side="left", padx=5)
                    
                    ctk.CTkButton(
                        backup_card,
                        text="📂 Show in Folder",
                        command=lambda b=backup_file: os.startfile(os.path.dirname(b)),
                        width=120,
                        height=25
                    ).pack(side="right", padx=10)
                    
                    ctk.CTkButton(
                        backup_card,
                        text="🗑️ Delete",
                        command=lambda b=backup_file: self.delete_backup(b),
                        width=70,
                        height=25,
                        fg_color="red"
                    ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            self.content,
            text="📁 Open Backups Folder",
            command=self.launcher.open_backups_folder,
            width=200
        ).pack(pady=10)
    
    def delete_backup(self, backup_file):
        """Delete a backup"""
        if messagebox.askyesno("Delete Backup", f"Delete {backup_file.name}?"):
            try:
                os.remove(backup_file)
                self.show_backups()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def show_settings(self):
        """Show settings view"""
        self.clear_content()
        
        ctk.CTkLabel(
            self.content,
            text="Settings",
            font=("Arial", 18, "bold")
        ).pack(pady=20)
        
        # Game executable path
        path_frame = ctk.CTkFrame(self.content)
        path_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            path_frame,
            text="Game Executable Path",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        path_entry = ctk.CTkEntry(path_frame, width=500)
        current_path = self.launcher.config.get("edu_exe_path", "") or self.launcher.edu_exe_path or ""
        path_entry.insert(0, current_path)
        path_entry.pack(padx=20, pady=5)
        
        btn_frame = ctk.CTkFrame(path_frame)
        btn_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Browse",
            command=lambda: self.browse_file(path_entry),
            width=80
        ).pack(side="left")
        
        # Worlds path
        worlds_frame = ctk.CTkFrame(self.content)
        worlds_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            worlds_frame,
            text="Worlds Folder Path",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        worlds_entry = ctk.CTkEntry(worlds_frame, width=500)
        worlds_path = self.launcher.config.get("worlds_path") or self.launcher.worlds_path or ""
        worlds_entry.insert(0, worlds_path)
        worlds_entry.pack(padx=20, pady=5)
        
        worlds_btn_frame = ctk.CTkFrame(worlds_frame)
        worlds_btn_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(
            worlds_btn_frame,
            text="Browse",
            command=lambda: self.browse_folder(worlds_entry),
            width=80
        ).pack(side="left")
        
        # Save button
        def save_settings():
            self.launcher.config["edu_exe_path"] = path_entry.get()
            self.launcher.config["worlds_path"] = worlds_entry.get()
            self.launcher.save_config()
            
            if os.path.exists(path_entry.get()):
                self.status_indicator.configure(text="✅ Game Found", text_color="green")
            else:
                self.status_indicator.configure(text="❌ Game Not Found", text_color="red")
            
            messagebox.showinfo("Success", "Settings saved!")
        
        ctk.CTkButton(
            self.content,
            text="Save Settings",
            command=save_settings,
            width=200
        ).pack(pady=20)
    
    def browse_file(self, entry_widget):
        """Browse for file"""
        filename = filedialog.askopenfilename(
            title="Select Minecraft Education Edition Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def browse_folder(self, entry_widget):
        """Browse for folder"""
        foldername = filedialog.askdirectory(
            title="Select Worlds Folder"
        )
        if foldername:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, foldername)
    
    def clear_content(self):
        """Clear content area"""
        for widget in self.content.winfo_children():
            widget.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

# Main entry point
if __name__ == "__main__":
    app = EduLauncherGUI()
    app.run()