import os
import sys
import json
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from jsonschema import validate, exceptions

level_list_schema = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

editors_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "role": {"type": "string"},
            "name": {"type": "number"},
            "link": {"type": "string"}
        }            
    }
}

level_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "author": {"type": "number"},
        "creators": {
            "type": "array",
            "items": {
                "type": "number",
            }
        },
        "verifier": {"type": "number"},
        "verification": {"type": "string"},
        "records": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "user": {"type": "number"},
                    "link": {"type": "string"},
                    "percent": {"type": "number"},
                    "hz": {"type": "number"},
                    "mobile": {"type": "boolean"}
                }
            }
        }
    }
}

pack_list_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "colour": {"type": "string"},
            "packs": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    }
}


def validate_data():
    validator = URLValidator()
    current_dir = os.path.join(os.getcwd(), "data")
    list_path = os.path.join(current_dir, "_list.json")
    pack_list_path = os.path.join(current_dir, "_packlist.json")
    name_map_path = os.path.join(current_dir, "_name_map.json")
    editors_path = os.path.join(current_dir, "_editors.json")
    had_error = False

    with open(list_path, "r", encoding='utf-8') as file:
        try:
            levels = json.load(file)
            validate(instance=levels, schema=level_list_schema)
        except ValueError as e:
            print(f"Invalid json in file _list.json: {str(e)}")
            sys.exit(1)
        except exceptions.ValidationError as e:
            print(f"Validation failed for _list.json: {str(e)}")
            sys.exit(1)

    with open(pack_list_path, "r", encoding='utf-8') as file:
        try:
            packs = json.load(file)
            validate(instance=packs, schema=pack_list_schema)
        except ValueError as e:
            print(f"Invalid json in file _packlist.json: {str(e)}")
            sys.exit(1)
        except exceptions.ValidationError as e:
            print(f"Validation failed for _packlist.json: {str(e)}")
            sys.exit(1)

    with open(name_map_path, "r", encoding='utf-8') as file:
        try:
            name_map = json.load(file)
        except ValueError as e:
            print(f"Invalid json in file _name_map.json: {str(e)}")
            sys.exit(1)

    def validate_user(user_id):
        return str(user_id) in name_map
    
    with open(editors_path, "r", encoding='utf-8') as file:
        try:
            editors = json.load(file)
            validate(instance=editors, schema=editors_schema)
        except ValueError as e:
            print(f"Invalid json in file _editors.json: {str(e)}")
            sys.exit(1)
        except exceptions.ValidationError as e:
            print(f"Validation failed for _editors.json: {str(e)}")
            sys.exit(1)

    level_ids = {}
    for filename in levels:
        file_path = os.path.join(current_dir, f"{filename}.json")
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    validate(instance=data, schema=level_schema)
                except ValueError as e:
                    print(f"Invalid json in file {filename}: {str(e)}")
                    had_error = True
                    continue
                except exceptions.ValidationError as e:
                    print(f"Validation failed for {filename}: {str(e)}")
                    had_error = True
                    continue
                    
                level_id = str(data["id"])
                
                if filename.endswith("2p"):
                    level_id += "2p"
                    
                if level_id in level_ids:
                    print(f"Duplicate gd level id in file {filename} with previous file {level_ids[level_id]}")
                    had_error = True
                    
                level_ids[level_id] = filename

                records = data["records"]
                names = [data["verifier"]]

                if not validate_user(data["verifier"]):
                    had_error = True
                    print(f"Invalid verifier: {filename}: {data['verifier']}")
                
                try:
                    validator(data["verification"])
                except ValidationError:
                    had_error = True
                    print(f"Invalid verification Url: {filename}: {data['verification']}")

                for record in records:

                    name = record["user"]
                    if name in names:
                        had_error = True
                        print(f"Duplicate Record: {filename}: {name}")

                    if not validate_user(name):
                        had_error = True
                        print(f"Invalid username: {filename}: {name}")

                    names.append(name)
                    url = record["link"]
                    try:
                        validator(url)
                    except ValidationError:
                        had_error = True
                        print(f"Invalid Url: {filename} {name}: {url}")

                creators = []
                for creator in data["creators"]:
                    if creator in creators:
                        had_error = True
                        print(f"Duplicate Creator: {filename}: {creator}")
                    if not validate_user(creator):
                        had_error = True
                        print(f"Invalid creator: {filename}: {creator}")

                    creators.append(creator)
        except FileNotFoundError:
            had_error = True
            print(f"Missing file {filename}")
            
    pack_names = []    
    for pack in packs:
        if pack["name"] in pack_names:
            had_error = True
            print(f"Duplicate pack name: \"{pack['name']}\"")
            continue
            
        pack_names.append(pack["name"])
        for level in pack["levels"]:
            if level not in levels:
                had_error = True
                print(f"Unkown level {level} in Pack \"{pack['name']}\"")
                
    for member in editors:
        if not validate_user(member["name"]):
            had_error = True
            print(f"Unknown editor: {member['name']} ({member['role']})")
    if had_error:
        sys.exit(1)

if __name__ == "__main__":
    validate_data()