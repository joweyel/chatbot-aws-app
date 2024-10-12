import os
import sys
import toml

def version(workspace):
    try:
        with open(os.path.join(workspace, "pyproject.toml"), "r", encoding="UTF-8") as file:
            pyproject_data = toml.load(file)
            return pyproject_data["project"]["version"]
    except FileNotFoundError:
        return "1unknown"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("unknown")
    else:
        workspace = sys.argv[1]
        print(version(workspace))