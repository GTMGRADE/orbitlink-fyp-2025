import logging
from typing import Dict, List
<<<<<<< HEAD
from flask import session
=======
>>>>>>> development
from entity.project import ProjectRepository, Project
import datetime

logger = logging.getLogger(__name__)


class ProjectsController:
<<<<<<< HEAD
<<<<<<<< HEAD:Controller/registeredUser_controller/projects_controller.py
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.repo = ProjectRepository(user_id)
========
    def get_user_id(self) -> str:
        """Get current user ID from session"""
        return session.get("user_id", "")

    def get_repo(self) -> ProjectRepository:
        """Get repository for current user"""
        return ProjectRepository(self.get_user_id())
>>>>>>>> development:Controller/projects_controller.py
=======
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.repo = ProjectRepository(user_id)
>>>>>>> development

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
<<<<<<< HEAD
<<<<<<<< HEAD:Controller/registeredUser_controller/projects_controller.py
=======
>>>>>>> development
        all_projects: List[Project] = self.repo.list()
        
        # Filter out projects without last_opened date
        projects_with_dates = [p for p in all_projects if p.last_opened]
        
<<<<<<< HEAD
========
        all_projects: List[Project] = self.get_repo().list()
>>>>>>>> development:Controller/projects_controller.py
=======
>>>>>>> development
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
<<<<<<< HEAD
        repo = self.get_repo()
        projects: List[Project] = repo.search(query) if query else repo.list()
=======
        projects: List[Project] = self.repo.search(query) if query else self.repo.list()
>>>>>>> development
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

<<<<<<< HEAD
<<<<<<<< HEAD:Controller/registeredUser_controller/projects_controller.py
    def create(self, name: str, description: str) -> Project | None:
        return self.repo.create(name, description)
========
    def create(self, name: str, description: str) -> Project:
        return self.get_repo().create(name, description)
>>>>>>>> development:Controller/projects_controller.py

    def open(self, pid: str) -> Project | None:
        return self.get_repo().open(pid)

    def rename(self, pid: str, new_name: str) -> Project | None:
        return self.get_repo().rename(pid, new_name)

    def archive(self, pid: str) -> Project | None:
        return self.get_repo().archive(pid)

<<<<<<<< HEAD:Controller/registeredUser_controller/projects_controller.py
    def delete(self, pid: int) -> bool:
        return self.repo.delete(pid)
========
    def delete(self, pid: str) -> bool:
        return self.get_repo().delete(pid)


projects_controller = ProjectsController()
>>>>>>>> development:Controller/projects_controller.py
=======
    def create(self, name: str, description: str) -> Project | None:
        return self.repo.create(name, description)

    def open(self, pid: str) -> Project | None:
        return self.repo.open(pid)

    def rename(self, pid: str, new_name: str) -> Project | None:
        return self.repo.rename(pid, new_name)

    def archive(self, pid: str) -> Project | None:
        return self.repo.archive(pid)

    def delete(self, pid: str) -> bool:
        return self.repo.delete(pid)
>>>>>>> development
