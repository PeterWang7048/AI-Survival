#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced Auto-Run Script - Implement fully automated game simulation
Features:
1. Set key game parameters via command line arguments
2. Automatically modify main.py file, inject parameters and auto-start code
3. Start game and monitor game progress
4. Detect game end and automatically close window
5. Restore original main.py file
"""

import argparse
import shutil
import os
import subprocess
import sys
import glob
import time
import re
import signal
import psutil

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Auto-run survival sandbox game simulation")
    
    # Add game parameters
    parser.add_argument("--seed", type=int, default=42, help="Map seed")
    parser.add_argument("--map_width", type=int, default=100, help="Map width")
    parser.add_argument("--map_height", type=int, default=100, help="Map height")
    parser.add_argument("--map_type", type=str, default="grassland", help="Map type")
    parser.add_argument("--resource_abundance", type=int, default=100, help="Resource abundance")
    parser.add_argument("--resource_regen", type=int, default=20, help="Resource regeneration rate")
    parser.add_argument("--game_duration", type=int, default=300, help="Game duration (number of rounds)")
    parser.add_argument("--animal_abundance_predator", type=int, default=100, help="Predator abundance")
    parser.add_argument("--animal_abundance_prey", type=int, default=100, help="Prey abundance")
    parser.add_argument("--group_hunt_frequency", type=int, default=30, help="Group hunt frequency")
    
    # Advanced ILAI settings
    parser.add_argument("--reasoning_attention", type=int, default=20, help="Reasoning attention percentage")
    parser.add_argument("--honesty_true", type=int, default=33, help="True information ratio")
    parser.add_argument("--honesty_false", type=int, default=33, help="False information ratio")
    parser.add_argument("--honesty_none", type=int, default=34, help="No sharing information ratio")
    
    return parser.parse_args()

def backup_main_py():
    """Backup original main.py file"""
    if os.path.exists("main.py.bak"):
        print("Backup file already exists, skipping backup")
    else:
        shutil.copy("main.py", "main.py.bak")
        print("Backed up main.py as main.py.bak")

def restore_main_py():
    """Restore original main.py file"""
    if os.path.exists("main.py.bak"):
        shutil.copy("main.py.bak", "main.py")
        print("Restored main.py")
    else:
        print("Backup file not found, cannot restore")

def modify_main_py_with_settings(settings_dict=None):
    """Modify main.py file, add auto-start game code and set game parameters"""
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Modify default values in settings dictionary
    if settings_dict:
        for key, value in settings_dict.items():
            # Use regex to replace values in settings dictionary
            if isinstance(value, str):
                pattern = f'"{key}":\\s*"[^"]*"'  # Match string values
                replacement = f'"{key}": "{value}"'
            else:
                pattern = f'"{key}":\\s*\\d+'  # Match numeric values
                replacement = f'"{key}": {value}'
                
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                print(f"Set {key} = {value}")
            else:
                print(f"Warning: Parameter {key} not found")
    
    # Add auto-start game and auto-close code
    if "root.mainloop()" in content:
        auto_code = """
    # Auto-start game
    def auto_start_and_monitor():
        app.start_game()
        
        # Function to check if game has ended
        def check_game_ended():
            if not hasattr(app, 'game') or app.game is None:
                root.after(1000, check_game_ended)
                return False
                
            # Check current turn number
            try:
                current_turn = getattr(app.game, 'current_turn', 0)
                if not current_turn:  # If no current_turn attribute, try other methods to get turn count
                    current_turn = getattr(app.game, 'turn', 0)
                
                max_turns = app.game.settings["game_duration"]
                if current_turn >= max_turns:
                    print(f"Reached maximum turns {max_turns}, auto-closing game")
                    root.after(1000, root.destroy)
                    return True
            except Exception as e:
                print(f"Error checking turns: {e}")
                
            # Check if all players are dead
            try:
                alive_players = 0
                for player in app.game.players:
                    if player.is_alive():
                        alive_players += 1
                
                if alive_players == 0:
                    print("All players dead, auto-closing game")
                    root.after(1000, root.destroy)
                    return True
            except Exception as e:
                print(f"Error checking player survival status: {e}")
                
            # Continue checking
            root.after(1000, check_game_ended)
            return False
        
        # Start monitoring
        root.after(2000, check_game_ended)
    
    # Auto-start after 1 second delay
    root.after(1000, auto_start_and_monitor)
    """
        
        new_content = content.replace(
            "root.mainloop()",
            auto_code + "\n    root.mainloop()"
        )
        
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully modified main.py, set parameters and added auto-start game code")
        return True
    else:
        print("Could not find suitable location to add auto-start code")
        return False

def get_latest_log_file():
    """Get latest log file"""
    log_files = glob.glob("game_*.log")
    if not log_files:
        return None
    
    # Sort by modification time, get latest log file
    latest_log = max(log_files, key=os.path.getmtime)
    return latest_log

def run_game_with_timeout(timeout=600):
    """Run modified game with timeout auto-termination"""
    print("Starting game...")
    
    # Use subprocess to start game
    process = subprocess.Popen([sys.executable, "main.py"])
    
    # Record start time
    start_time = time.time()
    
    # Record log files before running
    old_logs = set(glob.glob("game_*.log"))
    new_log_file = None
    
    try:
        while process.poll() is None:  # While process is still running
            # Check if timeout
            if time.time() - start_time > timeout:
                print(f"Game running exceeded {timeout} seconds, force terminating")
                kill_process_tree(process.pid)
                break
                
            # Check if new log files are generated
            current_logs = set(glob.glob("game_*.log"))
            new_logs = current_logs - old_logs
            if new_logs and not new_log_file:
                new_log_file = list(new_logs)[0]
                print(f"Detected new log file: {new_log_file}")
            
            # If there's a new log, check if it contains "Game ended"
            if new_log_file and os.path.exists(new_log_file):
                try:
                    with open(new_log_file, "r", encoding="utf-8") as f:
                        content = f.readlines()
                        # First check the last 50 lines
                        for line in content[-min(50, len(content)):]:
                            if "Game ended" in line or "游戏结束" in line:
                                print("Detected game end marker, log generated")
                                # Give game some time to complete log writing
                                time.sleep(5)
                                kill_process_tree(process.pid)
                                return new_log_file
                except Exception as e:
                    print(f"Error reading log file: {e}")
            
            # Check once per second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("User interrupted, terminating game")
        kill_process_tree(process.pid)
    
    # Return newly generated log file
    if new_log_file and os.path.exists(new_log_file):
        return new_log_file
    
    # Check again if there are new logs
    current_logs = set(glob.glob("game_*.log"))
    new_logs = current_logs - old_logs
    if new_logs:
        new_log_file = list(new_logs)[0]
        return new_log_file
        
    return None

def kill_process_tree(pid):
    """Terminate process and all its child processes"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except:
                pass
        parent.terminate()
        
        # Ensure processes are closed
        gone, still_alive = psutil.wait_procs(children + [parent], timeout=3)
        for p in still_alive:
            try:
                p.kill()
            except:
                pass
    except:
        # If using psutil fails, try using os.kill
        try:
            if os.name == 'nt':  # Windows
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
            else:  # Linux/MacOS
                os.kill(pid, signal.SIGTERM)
        except:
            print(f"Unable to terminate process {pid}")

def main():
    # 1. Parse command line arguments
    args = parse_arguments()
    settings_dict = vars(args)  # Convert command line arguments to dictionary
    
    # 2. Backup original main.py
    backup_main_py()
    
    try:
        # 3. Modify main.py
        if modify_main_py_with_settings(settings_dict):
            # 4. Run game
            log_file = run_game_with_timeout(timeout=600)  # 10 minute timeout
            
            # 5. Check results
            if log_file:
                print(f"Successfully generated log file: {log_file}")
                
                # Read last few lines of log, output result summary
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        result_section = False
                        results = []
                        
                        for line in lines:
                            if "|Rank|Player|Survival Days|" in line or "|排名|玩家|生存天数|" in line:
                                result_section = True
                                results.append(line)
                            elif result_section and line.strip():
                                results.append(line)
                        
                        if results:
                            print("\nGame Result Summary:")
                            for line in results[:11]:  # Only show header and top 10
                                print(line.strip())
                        
                except Exception as e:
                    print(f"Failed to read result summary: {e}")
            else:
                print("Run completed, but no new log file detected")
        
    finally:
        # 6. Restore original main.py
        restore_main_py()

if __name__ == "__main__":
    # Check if psutil is installed
    try:
        import psutil
    except ImportError:
        print("Missing psutil module, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
        
    main() 