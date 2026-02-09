import logging
from typing import Dict, List
from entity.project import ProjectRepository, Project
import datetime

logger = logging.getLogger(__name__)


class ProjectsController:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.repo = ProjectRepository(user_id)

    @staticmethod
    def _format_date(dt) -> str:
        if not dt:
            return "-"
        try:
            if isinstance(dt, str):
                # Handle string date
                return datetime.datetime.strptime(dt, "%Y-%m-%d").strftime("%d/%m/%y")
            elif isinstance(dt, datetime.datetime):
                # Handle datetime object
                return dt.strftime("%d/%m/%y")
            elif isinstance(dt, datetime.date):
                # Handle date object
                return dt.strftime("%d/%m/%y")
            else:
                return str(dt)
        except Exception:
            return str(dt)

    def view_recent(self) -> Dict:
        """View recent projects (limited to 3 most recently opened)"""
        all_projects: List[Project] = self.repo.list()
        
        # Filter out projects without last_opened date
        projects_with_dates = [p for p in all_projects if p.last_opened]
        
        # Sort by last_opened date (most recent first) and take top 3
        recent = sorted(
            projects_with_dates,
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

    def create(self, name: str, description: str) -> Project | None:
        return self.repo.create(name, description)

    def open(self, pid: str) -> Project | None:
        return self.repo.open(pid)

    def rename(self, pid: str, new_name: str) -> Project | None:
        return self.repo.rename(pid, new_name)

    def archive(self, pid: str) -> Project | None:
        return self.repo.archive(pid)

    def unarchive(self, pid: str) -> Project | None:
        return self.repo.unarchive(pid)

    def view_archived(self) -> Dict:
        """View archived projects"""
        projects: List[Project] = self.repo.list(include_archived=True)
        archived_projects = [p for p in projects if p.archived]
        
        vm = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "last_opened": self._format_date(p.last_opened),
            }
            for p in archived_projects
        ]
        
        return {
            "page_title": "Archived Projects",
            "projects": vm,
            "query": "",
        }

    def delete(self, pid: str) -> bool:
        return self.repo.delete(pid)