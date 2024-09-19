import os
import sys
import json
import random

current_dir = os.path.join(os.getcwd(), "data")
output_path = os.path.join(current_dir, "_name_map.json")

write_only_name_map = False

name_map={}
lookup_map={}

with open(output_path, 'r', encoding='utf-8') as file:
    name_map = json.load(file)

for key, value in name_map.items():
    lookup_map[value.lower()] = int(key)

id_digits = 10
id_lower = 10**(id_digits-1)
id_upper = 10**id_digits - 1

def get_id(username):
    username = username.strip()
    if username.lower() in lookup_map:
        return lookup_map[username.lower()]
        
    user_id = 0
    while user_id == 0:
        user_id = random.randint(id_lower, id_upper)
        if user_id in name_map:
            user_id = 0
            
    name_map[user_id] = username
    lookup_map[username.lower()] = user_id
    return user_id
    
def replace_users(names):
    for i in range(len(names)):
        if type(names[i]) == int:
            continue
                
        names[i] = get_id(names[i])

with open(os.path.join(current_dir, "_editors.json"), 'r+', encoding='utf-8') as file:
    editors = json.load(file)
    
    for member in editors:
        name = member['name']
        if type(name) == int:
            continue
        member['name'] = get_id(name)
    
    if not write_only_name_map:
        file.seek(0)
        json.dump(editors, file, ensure_ascii=False, indent="\t")
        file.truncate()

levels = []

with open(os.path.join(current_dir, "_list.json"), 'r', encoding='utf-8') as file:
    levels = json.load(file)
    
for level_name in levels:
    with open(os.path.join(current_dir, level_name + ".json"), 'r+', encoding='utf-8') as file:
        level = json.load(file)
        
        name = level['author']
        if type(name) != int:
            level['author'] = get_id(name)
            
        name = level['verifier']
        if type(name) != int:
            level['verifier'] = get_id(name)
        
        replace_users(level['creators'])
    
        for i in range(len(level['records'])):
            name = level['records'][i]['user']
            if type(name) == int:
                continue
            level['records'][i]['user'] = get_id(name)
    
        if not write_only_name_map:
            file.seek(0)
            json.dump(level, file, ensure_ascii=False, indent="\t")
            file.truncate()


name_map = dict(sorted(name_map.items(), key=lambda x: x[1]))

with open(output_path, 'w+', encoding='utf-8') as file:
    json.dump(name_map, file, ensure_ascii=False, indent="\t")
    print("Written names to file")