import logging
from typing import Dict, List
from flask import session
from entity.project import ProjectRepository, Project
import datetime

logger = logging.getLogger(__name__)


class ProjectsController:
    def get_user_id(self) -> str:
        """Get current user ID from session"""
        return session.get("user_id", "")

    def get_repo(self) -> ProjectRepository:
        """Get repository for current user"""
        return ProjectRepository(self.get_user_id())

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
        all_projects: List[Project] = self.get_repo().list()
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
        repo = self.get_repo()
        projects: List[Project] = repo.search(query) if query else repo.list()
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
        return self.get_repo().create(name, description)

    def open(self, pid: str) -> Project | None:
        return self.get_repo().open(pid)

    def rename(self, pid: str, new_name: str) -> Project | None:
        return self.get_repo().rename(pid, new_name)

    def archive(self, pid: str) -> Project | None:
        return self.get_repo().archive(pid)

    def delete(self, pid: str) -> bool:
        return self.get_repo().delete(pid)


projects_controller = ProjectsController()