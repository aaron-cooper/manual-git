import os

def get_ignore(root: str):
    ignore_paths = set(['.git'])
    if os.path.isfile(root + '/.gitlessignore'):
        with open(root + '/.gitlessignore', "r") as ignore_file:
            for line in ignore_file.readlines():
                line = line.strip()
                ignore_paths.add(line)
    return ignore_paths