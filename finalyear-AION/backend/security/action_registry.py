from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ActionRule:
    name: str
    capability: str
    agent: str
    destructive: bool = False


class AllowedActionRegistry:
    def __init__(self) -> None:
        self._rules: Dict[str, ActionRule] = {
            "create_folder": ActionRule("create_folder", "file_access", "FileAgent"),
            "create_file": ActionRule("create_file", "file_access", "FileAgent"),
            "combine_files": ActionRule("combine_files", "file_access", "FileAgent"),
            "find_files": ActionRule("find_files", "file_access", "FileAgent"),
            "list_directory": ActionRule("list_directory", "file_access", "FileAgent"),
            "move_file": ActionRule("move_file", "file_access", "FileAgent"),
            "move_files": ActionRule("move_files", "file_access", "FileAgent"),
            "copy_file": ActionRule("copy_file", "file_access", "FileAgent"),
            "rename_item": ActionRule("rename_item", "file_access", "FileAgent"),
            "rename_file": ActionRule("rename_file", "file_access", "FileAgent"),
            "delete_file": ActionRule("delete_file", "file_access", "FileAgent", True),
            "delete_item": ActionRule("delete_item", "file_access", "FileAgent", True),
            "open_in_explorer": ActionRule("open_in_explorer", "file_access", "FileAgent"),
            "open_application": ActionRule(
                "open_application", "application_access", "ApplicationAgent"
            ),
            "open_url": ActionRule("open_url", "browser_access", "BrowserAgent"),
            "search_web": ActionRule("search_web", "browser_access", "BrowserAgent"),
            "download_file": ActionRule("download_file", "browser_access", "BrowserAgent"),
            "verify": ActionRule("verify", "file_access", "FileAgent"),
        }

    def is_allowed(self, action: str) -> bool:
        return action in self._rules

    def get_rule(self, action: str) -> ActionRule:
        if action not in self._rules:
            raise ValueError(f"Action '{action}' is not allowlisted")
        return self._rules[action]

    def list_actions(self) -> list[dict]:
        return [
            {
                "action": rule.name,
                "capability": rule.capability,
                "agent": rule.agent,
                "destructive": rule.destructive,
            }
            for rule in self._rules.values()
        ]
