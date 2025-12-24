import logging
from typing import Dict, List
from entity.project import ProjectRepository, Project
import datetime

logger = logging.getLogger(__name__)


class ProjectsController:
    def __init__(self):
        self.repo = ProjectRepository()

    @staticmethod
    def _format_date(iso: str | None) -> str:
        if not iso:
            return "-"
        try:
            dt = datetime.date.fromisoformat(iso)
            return dt.strftime("%d/%m/%y")
        except Exception:
            return iso

    def view_recent(self) -> Dict:
        """View recent projects (limited to 3 most recently opened)"""
        all_projects: List[Project] = self.repo.list()
        # Sort by last_opened date (most recent first) and take top 3
        recent = sorted(
            [p for p in all_projects if p.last_opened],
            key=lambda x: x.last_opened,
            reverse=True
        )[:3]
        vm = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "last_opened": self._format_date(p.last_opened),
            }
            for p in recent
        ]
        return {
            "page_title": "Dashboard",
            "projects": vm,
            "query": "",
        }

    def view_all(self, query: str | None = None) -> Dict:
        projects: List[Project] = self.repo.search(query) if query else self.repo.list()
        vm = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "last_opened": self._format_date(p.last_opened),
            }
            for p in projects
        ]
        return {
            "page_title": "All Projects",
            "projects": vm,
            "query": (query or ""),
        }

    def create(self, name: str, description: str) -> Project:
        return self.repo.create(name, description)

    def open(self, pid: int) -> Project | None:
        return self.repo.open(pid)

    def rename(self, pid: int, new_name: str) -> Project | None:
        return self.repo.rename(pid, new_name)

    def archive(self, pid: int) -> Project | None:
        return self.repo.archive(pid)

    def delete(self, pid: int) -> bool:
        return self.repo.delete(pid)


projects_controller = ProjectsController()