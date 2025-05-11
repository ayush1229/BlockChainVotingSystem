import os

def list_files(startpath, ignore_folders):
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in ignore_folders]  # Exclude node_modules and env
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = " " * 4 * (level + 1)
        for file in files:
            print(f"{sub_indent}{file}")

list_files("D:/project/blockchainvotingsystem", ["node_modules", "env"])
# deployed to 0x39a18C3b330C4b14981dEBdF1D347c7a5727b61D