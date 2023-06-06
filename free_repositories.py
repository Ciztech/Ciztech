import os
from pathlib import Path
from typing import List, Final, Dict

REPO_LIST_PATH: Final[str] = "repo_list.txt"
REPO_PATH: Final[str] = "repos"


def clone(mirror, origin):
    folder = mirror.split("/")
    if len(folder) != 2:
        return
    _, name = folder
    name = name[:-4]
    if not os.path.exists(name):
        os.system(f"git clone {mirror}")
        os.chdir(name)
        os.system(f"git remote add epitech {origin}")
    else:
        os.chdir(name)
    os.system("git pull epitech main")
    os.system("git push origin main")
    os.chdir("..")


def main():
    os.makedirs(REPO_PATH, exist_ok=True)
    content = Path(REPO_LIST_PATH).read_text()
    lines = content.splitlines()
    os.chdir(REPO_PATH)
    for line in lines:
        target = line.split(" ")
        if len(target) != 2:
            continue
        origin, mirror = target
        clone(mirror, origin)
    os.chdir("..")


if __name__ == '__main__':
    main()
