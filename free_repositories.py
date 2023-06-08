import os
import json
import sys
from typing import Final

REPO_LIST_PATH: Final[str] = "repo_list.json"
REPO_PATH: Final[str] = "repos"
ORIGIN_KEY: Final[str] = "origin"
MIRROR_KEY: Final[str] = "mirror"
TEMPLATE_PATH: Final[str] = "/data/dev/Ciztech/template"
GIT_ATTRIBUTE_PATH: Final[str] = f"{TEMPLATE_PATH}/.gitattributes"


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
    if not os.path.exists(".gitattributes"):
        os.system(f"cp {GIT_ATTRIBUTE_PATH} .")
    os.system("git push origin main")
    os.chdir("..")


def all_mirror(content):
    for line in content:
        origin = line.get(ORIGIN_KEY)
        mirror = line.get(MIRROR_KEY)
        clone(mirror, origin)


def specific_mirror(content):
    for i in range(1, len(sys.argv)):
        for line in content:
            origin = line.get(ORIGIN_KEY)
            mirror = line.get(MIRROR_KEY)
            folder = mirror.split("/")
            if len(folder) != 2:
                return
            _, name = folder
            name = name[:-4]
            if name == sys.argv[i]:
                clone(mirror, origin)
                break


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
