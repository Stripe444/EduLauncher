# minecraft_edu_launcher.py
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import glob

class MinecraftEduLauncher:
    def __init__(self):
        self.base_dir = Path.home() / ".minecraft-edu-launcher"
        
        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.base_dir / "launcher_config.json"
        self.config = self.load_config()
        
        # Find Minecraft Education Edition installation
        self.edu_exe_path = self.find_education_edition()
        
        # Education Edition worlds location
        self.worlds_path = self.find_worlds_path()
        
    def find_education_edition(self) -> str:
        """Find Minecraft Education Edition executable"""
        possible_paths = [
            r"C:\Program Files\WindowsApps\Microsoft.MinecraftEducationEdition_1.21.13302.0_x64__8wekyb3d8bbwe\Minecraft.Windows.exe",
            r"C:\Program Files\WindowsApps\Microsoft.MinecraftEducationEdition_1.21.13302.0_x64__8wekyb3d8bbwe\MinecraftEducationEdition.exe",
        ]
        
        wildcard_paths = [
            r"C:\Program Files\WindowsApps\Microsoft.MinecraftEducationEdition_*\Minecraft.Windows.exe",
            r"C:\Program Files\WindowsApps\Microsoft.MinecraftEducationEdition_*\MinecraftEducationEdition.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        for pattern in wildcard_paths:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        
        if self.config.get("edu_exe_path") and os.path.exists(self.config["edu_exe_path"]):
            return self.config["edu_exe_path"]
        
        return None
    
    def find_worlds_path(self) -> str:
        """Find Education Edition worlds folder"""
        possible_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Packages\Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds"),
            os.path.expandvars(r"%APPDATA%\Minecraft Education Edition\games\com.mojang\minecraftWorlds"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        if self.config.get("worlds_path") and os.path.exists(self.config["worlds_path"]):
            return self.config["worlds_path"]
        
        return None
    
    def load_config(self) -> dict:
        """Load launcher configuration"""
        default_config = {
            "edu_exe_path": r"C:\Program Files\WindowsApps\Microsoft.MinecraftEducationEdition_1.21.13302.0_x64__8wekyb3d8bbwe\Minecraft.Windows.exe",
            "worlds_path": "",
            "theme": "dark",
            "close_launcher_on_play": False
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def launch_education_edition(self):
        """Launch Minecraft Education Edition directly"""
        edu_path = self.config.get("edu_exe_path") or self.edu_exe_path
        
        if not edu_path:
            raise Exception(
                "Minecraft Education Edition not found!\n\n"
                "Please go to Settings and set the correct path."
            )
        
        if not os.path.exists(edu_path):
            raise Exception(
                f"Minecraft Education Edition not found at:\n{edu_path}\n\n"
                "Please go to Settings and browse for the correct location."
            )
        
        try:
            subprocess.Popen([edu_path], shell=True)
            return True
        except PermissionError:
            raise Exception(
                "Permission denied! WindowsApps folder is protected.\n\n"
                "Try running this launcher as Administrator."
            )
        except Exception as e:
            raise Exception(f"Failed to launch: {str(e)}")
    
    def get_worlds(self) -> list:
        """Get list of worlds from Education Edition saves"""
        worlds = []
        worlds_path = self.config.get("worlds_path") or self.worlds_path
        
        if not worlds_path or not os.path.exists(worlds_path):
            return worlds
        
        try:
            for world_folder in os.listdir(worlds_path):
                world_dir = os.path.join(worlds_path, world_folder)
                if os.path.isdir(world_dir):
                    world_info = self.get_world_info(world_dir)
                    if world_info:
                        worlds.append(world_info)
        except PermissionError:
            pass
        
        worlds.sort(key=lambda x: x.get("last_played", ""), reverse=True)
        return worlds
    
    def get_world_info(self, world_path: str) -> dict:
        """Get information about a world"""
        world_name = os.path.basename(world_path)
        
        levelname_file = os.path.join(world_path, "levelname.txt")
        if os.path.exists(levelname_file):
            try:
                with open(levelname_file, 'r') as f:
                    world_name = f.read().strip()
            except:
                pass
        
        try:
            stat = os.stat(world_path)
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            size = self.get_folder_size(world_path)
        except:
            last_modified = None
            size = 0
        
        return {
            "folder": os.path.basename(world_path),
            "name": world_name,
            "path": world_path,
            "last_played": last_modified,
            "size_mb": round(size / (1024 * 1024), 2)
        }
    
    def get_folder_size(self, path: str) -> int:
        """Get folder size in bytes"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        except:
            pass
        return total
    
    def open_world_folder(self, world_path: str):
        """Open world folder in File Explorer"""
        if os.path.exists(world_path):
            subprocess.Popen(['explorer', world_path])
    
    def backup_world(self, world_path: str):
        """Backup a world to backups folder"""
        import shutil
        import zipfile
        
        backup_dir = self.base_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        world_name = os.path.basename(world_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"{world_name}_{timestamp}.zip"
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(world_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(world_path))
                    zipf.write(file_path, arcname)
        
        return str(backup_file)
    
    def open_backups_folder(self):
        """Open backups folder"""
        backup_dir = self.base_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        subprocess.Popen(['explorer', str(backup_dir)])
    
    def get_addons_path(self) -> str:
        """Get the addons folder path"""
        possible_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Packages\Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe\LocalState\games\com.mojang\resource_packs"),
            os.path.expandvars(r"%LOCALAPPDATA%\Packages\Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe\LocalState\games\com.mojang\behavior_packs"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return possible_paths[0] if possible_paths else ""
    
    def get_addons(self) -> list:
        """Get list of installed addons"""
        addons = []
        
        # Check resource packs
        rp_path = os.path.expandvars(r"%LOCALAPPDATA%\Packages\Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe\LocalState\games\com.mojang\resource_packs")
        if os.path.exists(rp_path):
            addons.extend(self._scan_addon_folder(rp_path, "resource_pack"))
        
        # Check behavior packs
        bp_path = os.path.expandvars(r"%LOCALAPPDATA%\Packages\Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe\LocalState\games\com.mojang\behavior_packs")
        if os.path.exists(bp_path):
            addons.extend(self._scan_addon_folder(bp_path, "behavior_pack"))
        
        # Check skin packs
        sp_path = os.path.expandvars(r"%LOCALAPPDATA%\Packages\Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe\LocalState\games\com.mojang\skin_packs")
        if os.path.exists(sp_path):
            addons.extend(self._scan_addon_folder(sp_path, "skin_pack"))
        
        return addons
    
    def _scan_addon_folder(self, folder_path: str, addon_type: str) -> list:
        """Scan a folder for addons"""
        addons = []
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                size = 0
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                elif os.path.isdir(item_path):
                    size = self.get_folder_size(item_path)
                
                addons.append({
                    "name": item,
                    "path": item_path,
                    "type": addon_type,
                    "size_mb": round(size / (1024 * 1024), 2)
                })
        except PermissionError:
            pass
        
        return addons
    
    def open_addon_folder(self, addon_path: str):
        """Open addon file/folder location"""
        if os.path.isfile(addon_path):
            subprocess.Popen(['explorer', '/select,', addon_path])
        elif os.path.isdir(addon_path):
            subprocess.Popen(['explorer', addon_path])