from __future__ import annotations

import asyncio
import json
import pathlib
import sys

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import (
    Final, TypedDict, List, Callable, Tuple, Coroutine, Any, Optional
)

PATH: Final[Path] = pathlib.Path.cwd()

REPO_LIST_PATH: Final[Path] = PATH / "repo_list.json"
REPO_PATH: Final[Path] = PATH / "repos"
TEMPLATE_PATH: Final[Path] = PATH / "template"

ORIGIN_KEY: Final[str] = "origin"
MIRROR_KEY: Final[str] = "mirror"
PATH_KEY: Final[str] = "path"


async def run(cmd: str) -> Tuple[bytes, bytes]:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    return await proc.communicate()


class RepoInfo(TypedDict):
    path: str
    mirror: str
    origin: Optional[str]


@dataclass
class Repo:
    path: Path
    mirror: str
    origin: Optional[str] = None

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
            origin=data_dict.get(ORIGIN_KEY),
            mirror=data_dict[MIRROR_KEY],
            path=Path(data_dict[PATH_KEY]),
        )

    async def make_mirror(self) -> None:
        path = pathlib.Path.cwd() / self.path / self.name

        if not path.exists():
            print(f"Cloning {self.name}")
            await run(f"git clone {self.mirror} {path} --recursive")

            if self.origin is not None:
                print(f"Registering remote: {self.name} -> {self.origin}")
                await run(f"git -C {path} remote add epitech {self.origin}")

        print(f"Pulling: {self.name}")
        await run(f"git -C {path} pull" + (" epitech main" * bool(self.origin)))

        if not ((path / ".gitattributes").is_file() or "stumper_" in self.name):
            print(f"Add gitattributes in {self.name}")
            await run(f"cp {TEMPLATE_PATH}/.gitattributes {path}")

        print(f"Pushing on: {self.name}")
        await run(f"git -C {path} push origin main")

    async def _clone_from_args(self) -> None:
        if self.name in sys.argv:
            await self.make_mirror()

    @property
    def clone(self) -> Callable[[], Coroutine[Any, Any, None]]:
        return (
            self.make_mirror
            if len(sys.argv) == 1 else
            self._clone_from_args
        )


async def main():
    with open(REPO_LIST_PATH) as f:
        content: List[RepoInfo] = json.load(f)

    marker = perf_counter()
    await asyncio.gather(
        *(Repo.from_dict(line).make_mirror() for line in content)
    )

    end = perf_counter()
    print(f"Took {(end - marker):.3f}s.")


if __name__ == '__main__':
    asyncio.run(main())
