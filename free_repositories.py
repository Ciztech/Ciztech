from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import (
    Final, TypedDict, List, Callable,
    Coroutine, Any, Optional
)


def setup_logger(logger_):
    logger_.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("mirrored.log")

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger_.addHandler(console_handler)
    logger_.addHandler(file_handler)
    return logger_


logger = setup_logger(logging.getLogger(__name__))

PATH: Final[Path] = pathlib.Path.cwd()

REPO_LIST_PATH: Final[Path] = PATH / "repo_list.json"
REPO_PATH: Final[Path] = PATH / "repos"
TEMPLATE_PATH: Final[Path] = PATH / "template"

ORIGIN_KEY: Final[str] = "origin"
MIRROR_KEY: Final[str] = "mirror"
PATH_KEY: Final[str] = "path"


async def run(cmd: str) -> bool:
    logger.info(f"Running: {cmd}")
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if stderr:
        logger.error(f"Failed command:\n{stderr.decode()}.")
        return True

    return False


class RepoInfo(TypedDict):
    path: str
    mirror: str
    origin: Optional[str]


class GitCmd:
    path = None

    @classmethod
    def at(cls, path: Path):
        cls.path = path
        return cls

    @classmethod
    async def run(cls, *args):
        command_base = "git"

        if cls.path is not None:
            command_base += f" -C {cls.path}"
            cls.path = None

        extras = ' '.join(args)
        await run(f"{command_base} {extras}")

    @classmethod
    async def clone(cls, url: str, path: Path, recursive: bool = True):
        await cls.run(f"clone {url} {path}" + (" --recursive" * recursive))

    @classmethod
    async def add_remote(cls, name: str, url: str):
        await cls.run(f"remote add {name} {url}")

    @classmethod
    async def pull(cls, origin: str):
        await cls.run("pull", origin or "origin main")

    @classmethod
    async def push(cls, origin: str):
        await cls.run("pull", origin)


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
        logger.info(f"Creating mirror of {self.name}")
        path = pathlib.Path.cwd() / self.path / self.name

        if not path.exists():
            await GitCmd.clone(self.mirror, path)

            if self.origin is not None:
                logger.info(f"Add remote to epitech: {self.origin}")
                await GitCmd.at(path).add_remote("epitech", self.origin)

        logger.info(f"Pulling {self.name}")
        logger.debug(f"origin: {self.origin}")
        await GitCmd.at(path).pull("epitech main" * bool(self.origin))

        if not (path / ".gitattributes").is_file() and "stumper_" not in self.name:
            logger.warning(f"Missing .gitattributes within {self.name}")
            await run(f"cp {TEMPLATE_PATH}/.gitattributes {path}")

        logger.info(f"Push on {self.name}")
        await GitCmd.at(path).push("origin main")

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
    logger.info(f"Took {(end - marker):.3f}s.")


if __name__ == '__main__':
    asyncio.run(main())
