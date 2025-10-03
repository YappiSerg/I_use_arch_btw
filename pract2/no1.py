#!/usr/bin/env python3
import os
import socket
import sys
import csv
import base64
import calendar
import datetime

def get_prompt():
    username = os.getlogin()
    hostname = socket.gethostname()
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")
    if current_dir.startswith(home_dir):
        current_dir = current_dir.replace(home_dir, "~", 1)
    return f"{username}@{hostname}:{current_dir}$ "

def cal(args):
    today = datetime.date.today()
    year = today.year
    month = today.month
    try:
        cal_text = calendar.month(year, month)
        print(cal_text)
    except Exception as e:
        print(f"Error displaying calendar: {e}")


def parser(uinput):
    parts = uinput.strip().split()
    if not parts:
        return None, []
    command = parts[0]
    args = parts[1:]
    return command, args

def set_script(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                script_commands = []
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    script_commands.append((line_num, line))
                print(f"current script: {path}")
                return script_commands
        except FileNotFoundError:
            sys.exit(1)
        except Exception as e:
            sys.exit(1)


def whoami(args):
    username = os.getlogin()
    print("Username:", username)
    hostname = socket.gethostname()
    print("Hostname:", hostname)
    current_dir = os.getcwd()
    print("Current directory:", current_dir)
    home_dir = os.path.expanduser("~")
    print("Home directory:", home_dir)


def ls(path):
    out = list_vfs(path)
    for i in out:
        print(i)

def cat(path):
    out = get_item(path)
    if out["type"] == "file":
        i = out["content"].split(";")
        for a in i:
            print(a)


def cd(path):
    global current_vfs_path
    current_vfs_path = path

def execution_script(path):
        print(f"execution: {path}")
        script_commands = get_item(path)
        if script_commands["type"] == "file":
            script_commands = script_commands["content"].split(";")
        for command_line in script_commands:
            print(f"{command_line}")
            command, args = parser(command_line)
            
            if command == "exit":
                break 
            execution_command(command, args)
            print()

def execution_command(command, args):
            try:
                if command is None:
                    pass
                if command == "exit":
                    pass
                elif command == "ls":
                    ls(args)
                elif command == "cal":
                    cal(args)
                elif command == "cd":
                    cd(args)
                elif command == "cat":
                    cat(args)
                elif command == "set_script":
                    current_script = set_script(args)
                elif command == "loadvfs":
                    loadvfs(args)
                elif command == "execution_script":
                    execution_script(args)
                elif command == "get_item":
                    print(get_item(args))
                elif command == "list_vfs":
                    print(list_vfs(args))
                elif command == "whoami":
                    whoami(args)
                elif command == "cp":
                    cp(args)
                else:
                    pass
            except KeyboardInterrupt:
                sys.exit(1)
            except EOFError:
                sys.exit(1)
            except Exception as e:
                print(e)

vfs_data = {}
current_vfs_path = "/"
vfs_physical_path = None

def loadvfs(args):
    global vfs_data, vfs_physical_path
    path = args[0] if args else None
    
    if not path:
        vfs_data = {
            "type": "directory",
            "name": "/",
            "content": {},
        }
        print("Created empty VFS")
        return True
    
    vfs_physical_path = path
    try:
        if not os.path.exists(path):
            vfs_data = create_vfs()
            print(f"File {path} not found, created empty VFS")
            return True
            
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            root = create_vfs()
            for line in reader:
                lpath = line['path']
                if not lpath.startswith('/'):
                    lpath = '/' + lpath
                if lpath == '/':
                    continue
                    
                parts = [p for p in lpath.split('/') if p]
                current_dir = root

                for part in parts[:-1]:
                    if part not in current_dir['content']:
                        current_dir['content'][part] = {
                            "type": "directory",
                            "name": part,
                            "content": {},
                        }
                    current_dir = current_dir['content'][part]
                
                filename = parts[-1]
                if line['type'] == 'directory':
                    current_dir['content'][filename] = {
                        "type": "directory",
                        "name": filename,
                        "content": {},
                    }
                else:
                    content = line.get('content', '')
                    if content:
                        try:
                            content = base64.b64decode(content).decode('utf-8')
                        except:
                            content = line['content']
                    
                    current_dir['content'][filename] = {
                        "type": "file",
                        "name": filename,
                        "content": content,
                    }
            
            vfs_data = root
            
        print(f"Loaded VFS from {path}")
        return True
        
    except Exception as e:
        print(f"Error loading VFS: {e}")
        vfs_data = create_vfs()
        return False


def create_vfs():
    return {
        "type": "directory",
        "name": "/",
        "content": {}
    }

def get_item(path):
    global vfs_data
    path = ''.join(path)
    if path == "/":
        return vfs_data
    
    parts = [p for p in path.split('/') if p]
    current = vfs_data
    
    for part in parts:
        if current['type'] != 'directory' or part not in current['content']:
            return None
        current = current['content'][part]
    
    return current

def list_vfs(path):
    item = get_item(path)
    if not item:
        return f"Path not found: {path}"
    
    if item['type'] != 'directory':
        return f"Not a directory: {path}"
    
    contents = list(item['content'].keys())
    return contents

#5

def cp(args):
    if len(args) < 2:
        print("Usage: cp <source> <destination>")
        return False
    
    source_path = args[0]
    dest_path = args[1]
    

    source_item = get_item(source_path)
    if not source_item:
        return False
    if source_item['type'] != 'file':
        return False

    dest_dir = get_item(dest_path)
    if not dest_dir:
        return False  
    if dest_dir['type'] != 'directory':
        return False 
    new_filename = source_item['name']
    
    if new_filename in dest_dir['content'].keys():
        print(f"File already exists: {new_filename}")
        return False
    
    dest_dir['content'][new_filename] = {
        "type": "file",
        "name": new_filename,
        "content": source_item['content']
    }
    
    print(f"Copied {source_path} to {dest_path}")
    return True



def main():
    while True:
        current_script = []
        prompt = get_prompt()
        try:
            user_input = input(prompt)
            command, args = parser(user_input)
            if command is None:
                continue
                
            if command == "exit":
                break
            elif command == "ls":
                ls(args)
            elif command == "cal":
                cal(args)
            elif command == "cd":
                cd(args)
            elif command == "cat":
                cat(args)
            elif command == "set_script":
                current_script = set_script(args)
            elif command == "execution_script":
                execution_script(args)
            elif command == "loadvfs":
                loadvfs(args)
            elif command == "get_item":
                print(get_item(args))
            elif command == "list_vfs":
                print(list_vfs(args))
            elif command == "whoami":
                whoami(args)
            elif command == "cp":
                cp(args)
            else:
                pass
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()