from pathlib import Path

from pypdf import PdfWriter

from backend.agents.file_agent import FileAgent
from backend.services.llm.interpreter import GoalInterpreter
from backend.security.action_registry import AllowedActionRegistry
from backend.security.permission_manager import PermissionManager


def _write_valid_pdf(path: Path, text: str):
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    path.write_bytes(b"")
    writer.write(path.open("wb"))
    path.write_bytes(path.read_bytes())

    page = writer.pages[0]
    page.add_transformation()
    # Re-generate the file cleanly so it is a valid PDF for pypdf to parse.
    path.unlink()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with path.open("wb") as f:
        writer.write(f)


def test_file_create_find_move_verify(tmp_path: Path):
    perm_manager = PermissionManager()
    agent = FileAgent(perm_manager)
    src_dir = tmp_path / "Downloads"
    src_dir.mkdir()
    pdf = src_dir / "a.pdf"
    pdf.write_text("x")

    found = agent.find_files(str(src_dir), ".pdf")
    assert found["details"]["count"] == 1

    created = agent.create_folder(str(src_dir), "AION_Demo")
    assert Path(created["path"]).exists()

    # Extract file paths from find results
    file_paths = [f["path"] for f in found["details"]["files"]]
    moved = agent.move_files(file_paths, str(src_dir / "AION_Demo"))
    assert moved["count"] == 1

    check = agent.verify_folder(str(src_dir / "AION_Demo"))
    assert check["details"]["exists"] and check["details"]["type"] == "folder"


def test_combine_pdfs_and_move_output(tmp_path: Path):
    perm_manager = PermissionManager()
    agent = FileAgent(perm_manager)

    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    desktop = tmp_path / "Desktop"
    desktop.mkdir()

    a = downloads / "A.pdf"
    b = downloads / "B.pdf"
    for pdf_path, label in [(a, "A"), (b, "B")]:
        writer = PdfWriter()
        page = writer.add_blank_page(width=200, height=200)
        page.merge_page(page)
        with pdf_path.open("wb") as f:
            writer.write(f)

    result = agent.combine_files([str(a), str(b)], str(downloads), "C.pdf")
    assert result["status"] == "COMPLETED"
    combined_path = downloads / "C.pdf"
    assert combined_path.exists()

    moved = agent.move_file(str(combined_path), str(desktop))
    assert moved["status"] == "COMPLETED"
    assert not combined_path.exists()
    assert (desktop / "C.pdf").exists()


def test_interpreter_and_registry_support_rename_and_explorer():
    interpreter = GoalInterpreter()
    parsed = interpreter.interpret("Rename AION_Demo to AION_Project.")
    assert any(task.action == "rename_item" for task in parsed.tasks)

    explorer_plan = interpreter.interpret("Open AION_Project in File Explorer.")
    assert any(task.action == "open_in_explorer" for task in explorer_plan.tasks)

    project_dir = Path.home() / "Downloads" / "AION_Project"
    project_dir.mkdir(exist_ok=True)
    target_file = project_dir / "test.txt"
    target_file.write_text("hello", encoding="utf-8")
    file_rename_plan = interpreter.interpret("Rename test.txt to AION_Test.txt inside AION_Project.")
    assert any(task.action == "rename_item" for task in file_rename_plan.tasks)
    assert "AION_Project" in str(file_rename_plan.tasks[0].parameters["source"])

    delete_plan = interpreter.interpret("Delete AION_Test.txt in AION_Project.")
    assert any(task.action == "delete_item" for task in delete_plan.tasks)
    assert "AION_Project" in str(delete_plan.tasks[0].parameters["path"])

    registry = AllowedActionRegistry()
    assert registry.is_allowed("rename_item")
    assert registry.is_allowed("open_in_explorer")
