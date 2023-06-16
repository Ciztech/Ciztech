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


def clone(mirror, origin):
    folder = mirror.split("/")
    if len(folder) != 2:
        return
    _, name = folder
    name = name[:-4]
    if not os.path.exists(name):
        os.system(f"git clone {mirror} --recursive")
        os.chdir(name)
        if origin:
            os.system(f"git remote add epitech {origin}")
    else:
        os.chdir(name)
    if origin:
        os.system("git pull epitech main")
    else:
        os.system("git pull")
    if not (os.path.exists(".gitattributes") or "stumper_" in name):
        os.system(f"cp {TEMPLATE_PATH}/.gitattributes .")
    os.system("git push origin main")
    os.chdir("..")


def all_mirror(content):
    for line in content:
        origin = line.get(ORIGIN_KEY)
        mirror = line.get(MIRROR_KEY)
        clone(mirror, origin)


def specific_mirror(content):
    for line in content:
        origin = line.get(ORIGIN_KEY)
        mirror = line.get(MIRROR_KEY)
        folder = mirror.split("/")
        if len(folder) != 2:
            return
        _, name = folder
        name = name[:-4]
        if name in sys.argv:
            clone(mirror, origin)


def main():
    os.makedirs(REPO_PATH, exist_ok=True)
    with open(REPO_LIST_PATH) as f:
        content = json.load(f)
    os.chdir(REPO_PATH)
    if len(sys.argv) == 1:
        all_mirror(content)
    else:
        specific_mirror(content)
    os.chdir("..")


if __name__ == '__main__':
    main()
