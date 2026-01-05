from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from db_config import get_connection


@dataclass
class Project:
    id: int
    user_id: int
    name: str
    description: str
    last_opened: Optional[date] = None
    archived: bool = False
    created_at: Optional[date] = None


class ProjectRepository:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def _to_project(self, row) -> Optional[Project]:
        """Convert database row to Project object"""
        if not row:
            return None
            
        try:
            return Project(
                id=row[0],
                user_id=row[1],
                name=row[2],
                description=row[3] if row[3] else "",
                last_opened=row[4],
                archived=bool(row[5]),
                created_at=row[6]
            )
        except Exception as e:
            print(f"Error converting row to project: {str(e)}")
            return None

    def list(self, include_archived: bool = False) -> List[Project]:
        """Get all projects for the current user"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            if include_archived:
                cursor.execute("""
                    SELECT * FROM projects 
                    WHERE user_id = %s 
                    ORDER BY last_opened DESC, created_at DESC
                """, (self.user_id,))
            else:
                cursor.execute("""
                    SELECT * FROM projects 
                    WHERE user_id = %s AND archived = FALSE
                    ORDER BY last_opened DESC, created_at DESC
                """, (self.user_id,))
            
            rows = cursor.fetchall()
            projects = []
            for row in rows:
                project = self._to_project(row)
                if project:
                    projects.append(project)
            return projects
            
        except Exception as e:
            print(f"Error listing projects: {str(e)}")
            return []
        finally:
            cursor.close()
            conn.close()

    def search(self, query: str) -> List[Project]:
        """Search projects by name or description"""
        if not query:
            return self.list()
            
        query = f"%{query}%"
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM projects 
                WHERE user_id = %s AND archived = FALSE 
                AND (name LIKE %s OR description LIKE %s)
                ORDER BY last_opened DESC
            """, (self.user_id, query, query))
            
            rows = cursor.fetchall()
            projects = []
            for row in rows:
                project = self._to_project(row)
                if project:
                    projects.append(project)
            return projects
            
        except Exception as e:
            print(f"Error searching projects: {str(e)}")
            return self.list()  # Fall back to listing all
        finally:
            cursor.close()
            conn.close()

    def get(self, pid: int) -> Optional[Project]:
        """Get a specific project by ID for the current user"""
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM projects 
                WHERE id = %s AND user_id = %s
            """, (pid, self.user_id))
            
            row = cursor.fetchone()
            return self._to_project(row)
            
        except Exception as e:
            print(f"Error getting project: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()

    def create(self, name: str, description: str) -> Optional[Project]:
        """Create a new project for the current user"""
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (user_id, name, description, last_opened)
                VALUES (%s, %s, %s, CURDATE())
            """, (self.user_id, name.strip(), description.strip()))
            
            conn.commit()
            project_id = cursor.lastrowid
            
            # Return the created project
            return self.get(project_id)
            
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def update(self, project: Project) -> bool:
        """Update an existing project"""
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE projects 
                SET name = %s, description = %s, last_opened = %s, archived = %s
                WHERE id = %s AND user_id = %s
            """, (project.name, project.description, 
                  project.last_opened, project.archived, 
                  project.id, self.user_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating project: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def open(self, pid: int) -> Optional[Project]:
        """Mark a project as opened (update last_opened date)"""
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE projects 
                SET last_opened = CURDATE()
                WHERE id = %s AND user_id = %s
            """, (pid, self.user_id))
            
            conn.commit()
            return self.get(pid)
            
        except Exception as e:
            print(f"Error opening project: {str(e)}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def rename(self, pid: int, new_name: str) -> Optional[Project]:
        """Rename a project"""
        project = self.get(pid)
        if not project:
            return None
        
        project.name = new_name.strip()
        if self.update(project):
            return project
        return None

    def archive(self, pid: int) -> Optional[Project]:
        """Archive a project"""
        project = self.get(pid)
        if not project:
            return None
        
        project.archived = True
        if self.update(project):
            return project
        return None

    def delete(self, pid: int) -> bool:
        """Delete a project"""
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM projects 
                WHERE id = %s AND user_id = %s
            """, (pid, self.user_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error deleting project: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()