# file_router.py
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".mp4")
PRIVATE_TRASH_NAME = "._trash-temp"


@dataclass(frozen=True)
class MoveResult:
    src: Path
    dst: Path


class FileRouter:
    def __init__(
        self,
        source_dir: Path,
        supported_exts: Iterable[str] = SUPPORTED_EXTENSIONS,
        private_trash_name: str = PRIVATE_TRASH_NAME,
    ):
        self.source_dir = Path(source_dir)
        self.supported_exts = tuple(e.lower() for e in supported_exts)
        self.private_trash_name = private_trash_name

    def list_media(self) -> list[Path]:
        return sorted(
            [
                p for p in self.source_dir.iterdir()
                if p.is_file() and p.suffix.lower() in self.supported_exts
            ]
        )

    def list_target_folders(self) -> list[Path]:
        return sorted(
            [
                p for p in self.source_dir.iterdir()
                if p.is_dir() and p.name != self.private_trash_name
            ]
        )

    def ensure_private_trash(self) -> Path:
        trash = self.source_dir / self.private_trash_name
        trash.mkdir(exist_ok=True)
        return trash

    def move(self, src: Path, target_folder: Path, *, on_collision: str = "error") -> MoveResult:
        """
        on_collision:
          - "error": raise FileExistsError
          - "rename": auto-rename to 'name (2).ext', etc.
        """
        src = Path(src)
        target_folder = Path(target_folder)

        if not target_folder.exists() or not target_folder.is_dir():
            raise NotADirectoryError(f"Target folder does not exist: {target_folder}")

        dst = target_folder / src.name

        if dst.exists():
            if on_collision == "error":
                raise FileExistsError(f"File already exists: {dst}")
            if on_collision == "rename":
                dst = self._unique_destination(target_folder, src.name)
            else:
                raise ValueError(f"Unknown on_collision mode: {on_collision}")

        shutil.move(str(src), str(dst))
        return MoveResult(src=src, dst=dst)

    def move_to_trash(self, src: Path, *, on_collision: str = "rename") -> MoveResult:
        trash = self.ensure_private_trash()
        return self.move(src, trash, on_collision=on_collision)

    def _unique_destination(self, folder: Path, filename: str) -> Path:
        base = Path(filename).stem
        ext = Path(filename).suffix
        candidate = folder / filename
        counter = 2
        while candidate.exists():
            candidate = folder / f"{base} ({counter}){ext}"
            counter += 1
        return candidate
