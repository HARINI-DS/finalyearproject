from __future__ import annotations

import re
from uuid import uuid4

from pydantic import ValidationError

from backend.core.config import settings
from backend.models.schemas import GoalInterpretation, TaskModel
from backend.services.llm.base_provider import BaseLLMProvider
from backend.services.llm.openai_provider import OpenAIProvider


class GoalInterpreter:
    def __init__(self, provider: BaseLLMProvider | None = None) -> None:
        self.provider = provider
        if not self.provider and settings.openai_api_key:
            self.provider = OpenAIProvider(api_key=settings.openai_api_key)

    @staticmethod
    def _resolve_location(goal: str, default: str = "Downloads") -> str:
        text = goal.lower()
        home = __import__("pathlib").Path.home()

        if "downloads" in text:
            return str((home / "Downloads").resolve())
        if "desktop" in text:
            return str((home / "Desktop").resolve())
        if "documents" in text:
            return str((home / "Documents").resolve())
        if "home" in text:
            return str(home.resolve())

        for token in ["downloads", "documents", "desktop", "home"]:
            match = re.search(rf"(?:in|on|inside|my)\s+(?:the\s+)?{token}(?:\s+folder)?", goal, flags=re.IGNORECASE)
            if match:
                if token == "downloads":
                    return str((home / "Downloads").resolve())
                if token == "documents":
                    return str((home / "Documents").resolve())
                if token == "desktop":
                    return str((home / "Desktop").resolve())
                if token == "home":
                    return str(home.resolve())

        # If the goal describes a folder path like "inside AION_Project", prefer that folder if it exists.
        inside_match = re.search(r"(?:inside|in)\s+([A-Za-z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
        if inside_match:
            candidate_name = inside_match.group(1)
            for base_name in ["Downloads", "Desktop", "Documents"]:
                candidate = (home / base_name / candidate_name).resolve()
                if candidate.exists() and candidate.is_dir():
                    return str(candidate)

        return str((home / default).resolve())

    def _heuristic_interpret(self, goal: str) -> GoalInterpretation:
        text = goal.lower()
        tasks: list[TaskModel] = []

        # Pattern 1: Create folder
        if ("create" in text or "make" in text) and ("folder" in text or "directory" in text):
            folder_match = re.search(r"(?:called|named)\s+([a-zA-Z0-9_\-]+)", goal, flags=re.IGNORECASE)
            folder_name = folder_match.group(1) if folder_match else "NewFolder"
            parent_dir = self._resolve_location(goal, "Downloads")

            tasks = [
                TaskModel(
                    id="task_1",
                    action="create_folder",
                    agent="FileAgent",
                    parameters={"parent": parent_dir, "name": folder_name},
                ),
                TaskModel(
                    id="task_2",
                    action="verify",
                    agent="FileAgent",
                    parameters={"path": str((__import__("pathlib").Path(parent_dir) / folder_name).resolve())},
                ),
            ]
            return GoalInterpretation(goal=f"Create folder '{folder_name}' in {__import__('pathlib').Path(parent_dir).name}", tasks=tasks)

        # Pattern 1.25: Create file
        if ("create" in text or "make" in text) and ("file" in text):
            file_match = re.search(r"(?:called|named)\s+([a-zA-Z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
            file_name = file_match.group(1) if file_match else "newfile.txt"

            home = __import__("pathlib").Path.home()
            parent_dir = self._resolve_location(goal, "Downloads")

            # If the user says "inside AION_Project", resolve the project folder as the parent directory.
            inside_match = re.search(r"(?:inside|in)\s+([A-Za-z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
            if inside_match:
                candidate_name = inside_match.group(1)
                for base in ["Downloads", "Desktop", "Documents"]:
                    candidate = (home / base / candidate_name).resolve()
                    if candidate.exists() and candidate.is_dir():
                        parent_dir = str(candidate)
                        break

            tasks = [
                TaskModel(
                    id="task_1",
                    action="create_file",
                    agent="FileAgent",
                    parameters={"parent": parent_dir, "name": file_name},
                ),
                TaskModel(
                    id="task_2",
                    action="verify",
                    agent="FileAgent",
                    parameters={"path": str((__import__("pathlib").Path(parent_dir) / file_name).resolve())},
                ),
            ]
            return GoalInterpretation(goal=f"Create file '{file_name}' in {__import__('pathlib').Path(parent_dir).name}", tasks=tasks)

        # Pattern 1.3: Combine files into output PDF
        if ("combine" in text or "merge" in text) and ("file" in text or "pdf" in text):
            parts = re.findall(r"(?:[A-Za-z0-9_\-\.]+\.(?:pdf|txt|docx|csv))", goal, flags=re.IGNORECASE)
            files = []
            for name in parts:
                if name.lower().endswith(".pdf"):
                    files.append(str((__import__("pathlib").Path.home() / "Downloads" / name).resolve()))
            if not files:
                files = [
                    str((__import__("pathlib").Path.home() / "Downloads" / "A.pdf").resolve()),
                    str((__import__("pathlib").Path.home() / "Downloads" / "B.pdf").resolve()),
                ]

            output_name = "combined.pdf"
            m = re.search(r"into\s+([A-Za-z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
            if m:
                output_name = m.group(1)
            if not output_name.lower().endswith(".pdf"):
                output_name = f"{output_name}.pdf"

            return GoalInterpretation(
                goal=f"Combine files into {output_name}",
                tasks=[
                    TaskModel(
                        id="task_1",
                        action="find_files",
                        agent="FileAgent",
                        parameters={"directory": str((__import__("pathlib").Path.home() / "Downloads").resolve()), "pattern": "*.pdf"},
                    ),
                    TaskModel(
                        id="task_2",
                        action="combine_files",
                        agent="FileAgent",
                        parameters={
                            "files": files,
                            "destination_directory": str((__import__("pathlib").Path.home() / "Downloads").resolve()),
                            "output_name": output_name,
                        },
                    ),
                    TaskModel(
                        id="task_3",
                        action="verify",
                        agent="FileAgent",
                        parameters={"path": str((__import__("pathlib").Path.home() / "Downloads" / output_name).resolve())},
                    ),
                ],
            )

        # Pattern 1.4: Move file from one place to another
        if ("move" in text or "transfer" in text) and ("file" in text or "pdf" in text or ".pdf" in text):
            file_match = re.search(r"([A-Za-z0-9_\-]+\.(?:pdf|txt|docx|csv))", goal, flags=re.IGNORECASE)
            file_name = file_match.group(1) if file_match else "A.pdf"
            source_dir = "Downloads"
            if "downloads" in text:
                source_dir = "Downloads"
            elif "desktop" in text:
                source_dir = "Desktop"
            elif "documents" in text:
                source_dir = "Documents"

            destination_dir = "Desktop"
            if "desktop" in text:
                destination_dir = "Desktop"
            elif "downloads" in text:
                destination_dir = "Downloads"
            elif "documents" in text:
                destination_dir = "Documents"

            source_path = str((__import__("pathlib").Path.home() / source_dir / file_name).resolve())
            destination_path = str((__import__("pathlib").Path.home() / destination_dir).resolve())
            if destination_dir.lower() == source_dir.lower():
                destination_path = source_path

            tasks = [
                TaskModel(
                    id="task_1",
                    action="move_file",
                    agent="FileAgent",
                    parameters={"source": source_path, "destination": destination_path},
                ),
                TaskModel(
                    id="task_2",
                    action="verify",
                    agent="FileAgent",
                    parameters={"path": str((__import__("pathlib").Path.home() / destination_dir / file_name).resolve())},
                ),
            ]
            return GoalInterpretation(goal=f"Move {file_name} from {source_dir} to {destination_dir}", tasks=tasks)

        # Pattern 1.5: Delete folder or file
        if any(x in text for x in ["delete", "remove", "rm"]):
            item_name = None
            item_match = re.search(r"(?:delete|remove|rm)\s+(?:the\s+)?([a-zA-Z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
            if item_match:
                item_name = item_match.group(1)

            if item_name:
                location = self._resolve_location(goal, "Downloads")

                # If a project folder is mentioned, prefer that folder for deletion.
                project_match = re.search(r"(?:in|inside|from)\s+([A-Za-z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
                if project_match:
                    project_name = project_match.group(1)
                    base_home = __import__("pathlib").Path.home()
                    candidate = (base_home / "Downloads" / project_name).resolve()
                    if candidate.exists() and candidate.is_dir():
                        location = str(candidate)

                item_path = str((__import__("pathlib").Path(location) / item_name).resolve())

                tasks = [
                    TaskModel(
                        id="task_1",
                        action="delete_item",
                        agent="FileAgent",
                        parameters={"path": item_path},
                    ),
                    TaskModel(
                        id="task_2",
                        action="verify",
                        agent="FileAgent",
                        parameters={"path": item_path},
                    ),
                ]
                return GoalInterpretation(goal=f"Delete {item_name} from {__import__('pathlib').Path(location).name}", tasks=tasks)

        # Pattern 1.6: Rename file or folder
        if "rename" in text:
            rename_match = re.search(r"rename\s+([A-Za-z0-9_\-\.]+)\s+(?:to|as)\s+([A-Za-z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
            if rename_match:
                source_name, new_name = rename_match.groups()
                location = self._resolve_location(goal, "Downloads")
                source_path = str((__import__("pathlib").Path(location) / source_name).resolve())

                tasks = [
                    TaskModel(
                        id="task_1",
                        action="rename_item",
                        agent="FileAgent",
                        parameters={"source": source_path, "new_name": new_name},
                    ),
                    TaskModel(
                        id="task_2",
                        action="verify",
                        agent="FileAgent",
                        parameters={"path": str((__import__("pathlib").Path(location) / new_name).resolve())},
                    ),
                ]
                return GoalInterpretation(goal=f"Rename {source_name} to {new_name}", tasks=tasks)

        # Pattern 1.7: Open in File Explorer
        if ("open" in text or "show" in text) and ("explorer" in text or "file explorer" in text):
            target_match = re.search(r"(?:open|show)\s+([A-Za-z0-9_\-\.]+)", goal, flags=re.IGNORECASE)
            target_name = target_match.group(1) if target_match else "Downloads"
            location = self._resolve_location(goal, "Downloads")
            target_path = str((__import__("pathlib").Path(location) / target_name).resolve())

            tasks = [
                TaskModel(
                    id="task_1",
                    action="open_in_explorer",
                    agent="FileAgent",
                    parameters={"path": target_path},
                )
            ]
            return GoalInterpretation(goal=f"Open {target_name} in File Explorer", tasks=tasks)

        # Pattern 2: PDF organization
        if "pdf" in text and "download" in text and ("move" in text or "organize" in text):
            folder_match = re.search(r"called\s+([a-zA-Z0-9_\-]+)", goal)
            folder_name = folder_match.group(1) if folder_match else "AION_Demo"
            downloads = str((__import__("pathlib").Path.home() / "Downloads").resolve())

            tasks = [
                TaskModel(
                    id="task_1",
                    action="find_files",
                    agent="FileAgent",
                    parameters={"directory": downloads, "extension": ".pdf"},
                ),
                TaskModel(
                    id="task_2",
                    action="create_folder",
                    agent="FileAgent",
                    parameters={"parent": downloads, "name": folder_name},
                ),
                TaskModel(
                    id="task_3",
                    action="move_files",
                    agent="FileAgent",
                    parameters={
                        "files": "__from_task_1__",
                        "destination_directory": str(
                            (__import__("pathlib").Path(downloads) / folder_name).resolve()
                        ),
                    },
                ),
                TaskModel(
                    id="task_4",
                    action="verify",
                    agent="FileAgent",
                    parameters={"path": str((__import__("pathlib").Path(downloads) / folder_name).resolve())},
                ),
            ]
            return GoalInterpretation(goal="Organize PDF files in Downloads", tasks=tasks)

        # Pattern 3: Chrome web search
        if "open" in text and "chrome" in text and "search" in text:
            query = goal.split("search for")[-1].strip(" .") if "search for" in text else goal
            tasks = [
                TaskModel(
                    id="task_1",
                    action="search_web",
                    agent="BrowserAgent",
                    parameters={"query": query},
                )
            ]
            return GoalInterpretation(goal="Search web in Chrome", tasks=tasks)

        # Pattern 4: Open VS Code
        if "open" in text and "vs code" in text:
            tasks = [
                TaskModel(
                    id="task_1",
                    action="open_application",
                    agent="ApplicationAgent",
                    parameters={"name": "vs code"},
                )
            ]
            return GoalInterpretation(goal="Open VS Code", tasks=tasks)

        # Default: list home directory
        return GoalInterpretation(
            goal=goal,
            tasks=[
                TaskModel(
                    id=f"task_{uuid4().hex[:8]}",
                    action="list_directory",
                    agent="FileAgent",
                    parameters={"directory": str((__import__("pathlib").Path.home()).resolve())},
                )
            ],
        )

    def interpret(self, goal: str) -> GoalInterpretation:
        if not self.provider:
            return self._heuristic_interpret(goal)

        system_prompt = (
            "Convert user goal to strict JSON with keys goal and tasks. "
            "Each task requires id, action, agent, parameters. "
            "Use only allowlisted actions."
        )

        try:
            data = self.provider.complete_json(system_prompt=system_prompt, user_prompt=goal)
            return GoalInterpretation.model_validate(data)
        except (ValidationError, Exception):
            return self._heuristic_interpret(goal)
