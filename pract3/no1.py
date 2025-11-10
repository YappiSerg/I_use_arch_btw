#!/usr/bin/env python3
import os
import socket
import requests
import sys
import csv
import base64
import calendar
import datetime
import graphviz

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
        base_url = "https://api.nuget.org/v3-flatcontainer"
        package_url = f"{base_url}/{package_name.lower()}/{package_version}/{package_name.lower()}.nuspec"
        
        print(f"Запрос: {package_url}")
        
        response = requests.get(package_url)
        if response.status_code != 200:
            print(f"Ошибка: не удалось получить данные (статус {response.status_code})")
            return

        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        ns = {'ns': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}
        
        dependencies = root.find('.//ns:dependencies', ns)
        if dependencies is None:
            print("Нет зависимостей.")
            return

        print(f"\nЗависимости пакета {package_name} ({package_version}):\n")
        
        for group in dependencies.findall('ns:group', ns):
            target_framework = group.get('targetFramework', 'any')
            for dep in group.findall('ns:dependency', ns):
                dep_id = dep.get('id')
                dep_version = dep.get('version', '')
                print(f" - {dep_id} {dep_version} ({target_framework})")
        
        for dep in dependencies.findall('ns:dependency', ns):
            if dep.get('id') and not dependencies.find(f'ns:group/ns:dependency[@id="{dep.get("id")}"]', ns):
                dep_id = dep.get('id')
                dep_version = dep.get('version', '')
                print(f" - {dep_id} {dep_version} (any)")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

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

def get_dependencies_for_graph(package_name, package_version):
    try:
        base_url = "https://api.nuget.org/v3-flatcontainer"
        package_url = f"{base_url}/{package_name.lower()}/{package_version}/{package_name.lower()}.nuspec"
        
        response = requests.get(package_url)
        if response.status_code != 200:
            return []

        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        ns = {'ns': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}
        
        dependencies = root.find('.//ns:dependencies', ns)
        if dependencies is None:
            return []

        deps_list = []
        
        for group in dependencies.findall('ns:group', ns):
            target_framework = group.get('targetFramework', 'any')
            for dep in group.findall('ns:dependency', ns):
                dep_id = dep.get('id')
                dep_version = dep.get('version', '')
                if dep_id:
                    deps_list.append((dep_id, dep_version, target_framework))
        
        for dep in dependencies.findall('ns:dependency', ns):
            dep_id = dep.get('id')
            dep_version = dep.get('version', '')
            if dep_id and not any(d[0] == dep_id for d in deps_list):
                deps_list.append((dep_id, dep_version, 'any'))

        return deps_list

    except Exception as e:
        print(f"Ошибка получения зависимостей для {package_name}: {e}")
        return []

def print_graph(package_name, package_version, max_depth=3):
    """Основная функция для построения и отображения графа зависимостей"""
    try:
        dot = graphviz.Digraph(comment=f'Dependencies for {package_name}')
        dot.attr(rankdir='TB')
        
        def build_graph(current_package, current_version, depth=0, visited=None):
            if visited is None:
                visited = set()
            
            if depth > max_depth:
                return
            
            node_id = f"{current_package}_{current_version}"
            
            if node_id in visited:
                return
            
            visited.add(node_id)
            
            dot.node(node_id, f"{current_package}\n{current_version}")
            
            dependencies = get_dependencies_for_graph(current_package, current_version)
            
            for dep_name, dep_version, target_framework in dependencies:
                if depth + 1 <= max_depth:
                    dep_node_id = f"{dep_name}_{dep_version}"
                    
                    build_graph(dep_name, dep_version, depth + 1, visited)
                    
                    dot.edge(node_id, dep_node_id, label=target_framework)
        
        build_graph(package_name, package_version)
        
        output_file = params.get('output_image', 'dependency_graph').replace('.png', '')
        dot.render(output_file, view=True, format='png', cleanup=True)
        print(f"Граф зависимостей сохранен в {output_file}.png")
        
        return dot
    except Exception as e:
        print(f"Ошибка при построении графа: {e}")
        import traceback
        traceback.print_exc()
        return None

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
            elif command == "get_dependencies":
                get_dependencies(params['package_name'], params['package_version'], params['repository_url'])
            elif command == "print_graph":
                print_graph(params['package_name'], params['package_version'], params['max_depth'])
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
