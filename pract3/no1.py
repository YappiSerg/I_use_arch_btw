#!/usr/bin/env python3
import os
import socket
import requests
import sys
import csv
import base64
import calendar
import datetime


def parser(uinput):
    parts = uinput.strip().split()
    if not parts:
        return None, []
    command = parts[0]
    args = parts[1:]
    return command, args

def get_prompt():
    username = os.getlogin()
    hostname = socket.gethostname()
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")
    if current_dir.startswith(home_dir):
        current_dir = current_dir.replace(home_dir, "~", 1)
    return f"{username}@{hostname}:{current_dir}$ "

def set_param(args):
    if len(args) < 2:
        return
    
    param_name = args[0]
    param_value = ' '.join(args[1:])
    
    if param_name not in params:
        print("нет параметра")
        return
    
    if param_name == 'ascii_tree':
        if param_value.lower() in ['true', 'yes', 'y', '1']:
            params[param_name] = True
        elif param_value.lower() in ['false', 'no', 'n', '0']:
            params[param_name] = False
        else:
            print("Ошибка значения")
            return
    elif param_name == 'max_depth':
        try:
            params[param_name] = int(param_value)
        except ValueError:
            print("Ошибка значения")
            return
    else:
        params[param_name] = param_value
    
    print(f"Параметр '{param_name}' установлен в '{param_value}'")


def get_dependencies(package_name, package_version, repository_url):
    try:
        base_url = repository_url.rstrip('/')
        api_url = f"{base_url}/registration5-gz-semver2/{package_name.lower()}/{package_version}.json"

        response = requests.get(api_url)
        if response.status_code != 200:
            print("Нет данных о пакете")
            return

        data = response.json()
        catalog_entry = data.get("catalogEntry", {})
        deps = []

        for group in catalog_entry.get("dependencyGroups", []):
            framework = group.get("targetFramework", "any")
            group_deps = group.get("dependencies", [])
            if not group_deps:
                continue

            for dep in group_deps:
                deps.append({
                    "framework": framework,
                    "id": dep["id"],
                    "version_range": dep.get("range", "")
                })

        if not deps:
            print("Нет прямых зависимостей.")
            return

        print(f"\nЗависимости пакета {package_name} ({package_version}):\n")
        for d in deps:
            print(f" - {d['id']} {d['version_range']} ({d['framework']})")

        return deps

    except Exception as e:
        print(f"Ошибка: {e}")

params = {
    'package_name': '',
    'repository_url': '',
    'repository_mode': 'remote',
    'package_version': '',
    'output_image': 'dependency_graph.png',
    'ascii_tree': False,
    'max_depth': 3
}

def show_params():
    for key, value in params.items():
        print(f"{key}: {value}")

def main():
    while True:
        try:
            prompt = get_prompt()
            user_input = input(prompt)
            command, args = parser(user_input)
            if command is None:
                continue
            elif command == "show_params":
                show_params()
            elif command == "set":
                set_param(args)
            elif command = "get_dependencies":
                get_dependencies(params['package_name'], params['repository_url'], params['package_version'])
            if command == "exit":
                break
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