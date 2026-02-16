from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Literal, Union
import shutil

ActionType = Literal["move", "delete"]

@dataclass
class UndoAction:
    type: ActionType
    src: Path   # where the file currently is
    dst: Path   # where to restore it to

class UndoManager:
    def __init__(self) -> None:
        self._stack: List[UndoAction] = []

    def clear(self) -> None:
        self._stack.clear()

    def has_actions(self) -> bool:
        return bool(self._stack)

    def push_move(self, moved_to: Path, restore_to: Path) -> None:
        """
        File was moved to `moved_to` (destination).
        Undo should move it back to `restore_to` (original location).
        """
        self._stack.append(UndoAction(type="move", src=moved_to, dst=restore_to))

    def push_delete(self, moved_to: Path, restore_to: Path) -> None:
        """
        File was moved to trash/private location `moved_to`.
        Undo should move it back to `restore_to`.
        """
        self._stack.append(UndoAction(type="delete", src=moved_to, dst=restore_to))

    def undo(self) -> Optional[UndoAction]:
        if not self._stack:
            return None
        return self._stack.pop()

    def apply(self, action: UndoAction) -> None:
        """
        Execute the actual filesystem undo operation.
        """
        shutil.move(action.src, action.dst)
