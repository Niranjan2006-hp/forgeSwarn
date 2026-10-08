import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger("forgeswarm.workspace")

class ProjectWorkspace:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.root_path = Path(settings.WORKSPACE_ROOT).resolve() / project_id
        
    def initialize(self) -> Path:
        """Create clean workspace directory structure with valid python packages"""
        self.root_path = self.root_path.resolve()
        if self.root_path.exists():
            shutil.rmtree(self.root_path, ignore_errors=True)
            
        (self.root_path / "app" / "routers").mkdir(parents=True, exist_ok=True)
        (self.root_path / "app" / "services").mkdir(parents=True, exist_ok=True)
        (self.root_path / "app" / "static").mkdir(parents=True, exist_ok=True)
        (self.root_path / "tests").mkdir(parents=True, exist_ok=True)
        
        # Touch __init__.py files
        (self.root_path / "app" / "__init__.py").write_text("", encoding="utf-8")
        (self.root_path / "app" / "routers" / "__init__.py").write_text("", encoding="utf-8")
        (self.root_path / "app" / "services" / "__init__.py").write_text("", encoding="utf-8")
        (self.root_path / "tests" / "__init__.py").write_text("", encoding="utf-8")
        return self.root_path

    def write_file(self, relative_path: str, content: str) -> Path:
        file_path = self.root_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def read_file(self, relative_path: str) -> Optional[str]:
        file_path = self.root_path / relative_path
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def file_exists(self, relative_path: str) -> bool:
        return (self.root_path / relative_path).exists()

    def list_files(self) -> List[str]:
        if not self.root_path.exists():
            return []
        files = []
        for path in self.root_path.rglob("*"):
            if path.is_file() and not any(part.startswith(".") for part in path.parts):
                files.append(str(path.relative_to(self.root_path)).replace("\\", "/"))
        return sorted(files)
