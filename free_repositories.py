from __future__ import annotations

import os
import json
import sys
import pathlib
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypedDict, List, Callable


PATH: Final[Path] = pathlib.Path.cwd()

REPO_LIST_PATH: Final[Path] = PATH / "repo_list.json"
REPO_PATH: Final[Path] = PATH / "repos"
TEMPLATE_PATH: Final[Path] = PATH / "template"

ORIGIN_KEY: Final[str] = "origin"
MIRROR_KEY: Final[str] = "mirror"
PATH_KEY: Final[str] = "path"


class RepoInfo(TypedDict):
    path: str
    origin: str
    mirror: str


@dataclass
class Repo:
    path: Path
    origin: str
    mirror: str

    @property
    def name(self) -> str:
        folder = self.mirror.split("/")

        if len(folder) != 2:
            return "Unknown"

        _, name = folder
        return name[:-4]

    @classmethod
    def from_dict(cls, data_dict: RepoInfo) -> Repo:
        return cls(
            origin=data_dict[ORIGIN_KEY],
            mirror=data_dict[MIRROR_KEY],
            path=Path(data_dict[PATH_KEY]),
        )

    def make_mirror(self) -> None:
        path = pathlib.Path.cwd() / self.path / self.name

        if not path.exists():
            os.system(f"git clone {self.mirror} {path} --recursive")
            if self.origin:
                os.system(f"git -C {path} remote add epitech {self.origin}")

        if self.origin:
            os.system(f"git -C {path} pull epitech main")
        else:
            os.system(f"git -C {path} pull")

        if not ((path / ".gitattributes").is_file() or "stumper_" in self.name):
            os.system(f"cp {TEMPLATE_PATH}/.gitattributes {path}")

        os.system(f"git -C {path} push origin main")

    def _clone_from_args(self) -> None:
        if self.name in sys.argv:
            self.make_mirror()

    @property
    def clone(self) -> HandlerFunc:
        return (
            self.make_mirror
            if len(sys.argv) == 1 else
            self._clone_from_args
        )


HandlerFunc = Callable[[Repo], None]


def main():
    with open(REPO_LIST_PATH) as f:
        content: List[RepoInfo] = json.load(f)

    for line in content:
        repo = Repo.from_dict(line)
        repo.make_mirror()


if __name__ == '__main__':
    main()
