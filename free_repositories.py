import os
import json
import sys
from typing import Final

PATH: Final[str] = "/data/dev/Ciztech"

REPO_LIST_PATH: Final[str] = f"{PATH}/repo_list.json"
REPO_PATH: Final[str] = f"{PATH}/repos"
TEMPLATE_PATH: Final[str] = f"{PATH}/template"

ORIGIN_KEY: Final[str] = "origin"
MIRROR_KEY: Final[str] = "mirror"
PATH_KEY: Final[str] = "path"


def clone(mirror, origin, path):
    folder = mirror.split("/")
    if len(folder) != 2:
        return
    _, name = folder
    name = name[:-4]
    if not os.path.exists(name):
        os.system(f"git clone {mirror} {path}/{name} --recursive")
        os.chdir(f"{path}/{name}")
        if origin:
            os.system(f"git remote add epitech {origin}")
    else:
        os.chdir(f"{path}/{name}")
    if origin:
        os.system("git pull epitech main")
    else:
        os.system("git pull")
    if not (os.path.exists(".gitattributes") or "stumper_" in name):
        os.system(f"cp {TEMPLATE_PATH}/.gitattributes .")
    os.system("git push origin main")
    count = f"{path}/{name}".count('/')
    os.chdir("/".join((".." for _ in range (count + 1))))


def all_mirror(content):
    for line in content:
        origin = line.get(ORIGIN_KEY)
        mirror = line.get(MIRROR_KEY)
        path = line.get(PATH_KEY)
        clone(mirror, origin, path)


def specific_mirror(content):
    for line in content:
        origin = line.get(ORIGIN_KEY)
        mirror = line.get(MIRROR_KEY)
        path = line.get(PATH_KEY)
        folder = mirror.split("/")
        if len(folder) != 2:
            return
        _, name = folder
        name = name[:-4]
        if name in sys.argv:
            clone(mirror, origin, path)


def main():
    os.makedirs(REPO_PATH, exist_ok=True)
    with open(REPO_LIST_PATH) as f:
        content = json.load(f)
    if len(sys.argv) == 1:
        all_mirror(content)
    else:
        specific_mirror(content)


if __name__ == '__main__':
    main()
