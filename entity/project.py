import json
import os
import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "projects.json")


@dataclass
class Project:
    id: int
    name: str
    description: str
    last_opened: Optional[str] = None  # ISO date string
    archived: bool = False

    def touch_opened(self) -> None:
        self.last_opened = datetime.date.today().isoformat()


class ProjectRepository:
    def __init__(self, path: str = DATA_FILE) -> None:
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._seed()

    def _seed(self) -> None:
        sample = [
            asdict(Project(id=1, name="Project Name 1", description="Demo project", last_opened=datetime.date.today().isoformat())),
            asdict(Project(id=2, name="Project Name 2", description="Another project", last_opened=datetime.date.today().isoformat())),
            asdict(Project(id=3, name="Project Name 3", description="Sample notes", last_opened=datetime.date.today().isoformat())),
            asdict(Project(id=4, name="October Project 1", description="Old project from October", last_opened="2025-10-15")),
            asdict(Project(id=5, name="October Project 2", description="Another old project", last_opened="2025-10-20")),
            asdict(Project(id=6, name="October Project 3", description="October archive", last_opened="2025-10-05")),
        ]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2)

    def _read(self) -> List[Project]:
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Project(**p) for p in data]

    def _write(self, projects: List[Project]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([asdict(p) for p in projects], f, indent=2)

    def list(self, include_archived: bool = False) -> List[Project]:
        projects = self._read()
        return [p for p in projects if include_archived or not p.archived]

    def search(self, query: str) -> List[Project]:
        q = (query or "").strip().lower()
        return [p for p in self.list() if q in p.name.lower() or q in p.description.lower()]

    def create(self, name: str, description: str) -> Project:
        projects = self._read()
        next_id = (max((p.id for p in projects), default=0) + 1)
        project = Project(id=next_id, name=name.strip(), description=description.strip())
        project.touch_opened()
        projects.append(project)
        self._write(projects)
        return project

    def get(self, pid: int) -> Optional[Project]:
        for p in self._read():
            if p.id == pid:
                return p
        return None

    def save(self, project: Project) -> None:
        projects = self._read()
        for i, p in enumerate(projects):
            if p.id == project.id:
                projects[i] = project
                break
        self._write(projects)

    def open(self, pid: int) -> Optional[Project]:
        p = self.get(pid)
        if not p:
            return None
        p.touch_opened()
        self.save(p)
        return p

    def rename(self, pid: int, new_name: str) -> Optional[Project]:
        p = self.get(pid)
        if not p:
            return None
        p.name = new_name.strip()
        self.save(p)
        return p

    def archive(self, pid: int) -> Optional[Project]:
        p = self.get(pid)
        if not p:
            return None
        p.archived = True
        self.save(p)
        return p

    def delete(self, pid: int) -> bool:
        projects = self._read()
        filtered = [p for p in projects if p.id != pid]
        if len(filtered) == len(projects):
            return False
        self._write(filtered)
        return True