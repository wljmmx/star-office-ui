    def load_all_agents(self) -> List[Agent]:
        """Load all agents from database with project associations."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Load agents with project info
            cursor.execute("""
                SELECT a.id, a.name, a.pixel_character, a.avatar_url, a.role, a.status, 
                       a.current_task_id, a.project_id, a.project_name, a.project_url,
                       a.created_at, a.updated_at
                FROM agents a
                ORDER BY a.id
            """)
            agent_rows = cursor.fetchall()
            
            # Load tasks with project info
            cursor.execute("""
                SELECT t.id, t.title, t.status, t.progress, t.assigned_to, 
                       t.project_id, t.project_name, t.project_url,
                       t.created_at, t.updated_at
                FROM tasks t
            """)
            task_rows = cursor.fetchall()
            
            # Load all projects
            cursor.execute("""
                SELECT id, name, github_url, description, status, work_dir, 
                       created_at, updated_at
                FROM projects
            """)
            project_rows = cursor.fetchall()
            
            # Create projects map
            projects_map = {}
            for row in project_rows:
                project = Project.from_db(dict(zip(
                    ['id', 'name', 'github_url', 'description', 'status', 'work_dir', 'created_at', 'updated_at'],
                    row
                )))
                projects_map[project.project_id] = project
            
            # Create tasks map
            tasks_map = {}
            for row in task_rows:
                task_dict = dict(zip(
                    ['id', 'title', 'status', 'progress', 'assigned_to', 'project_id', 'project_name', 'project_url', 'created_at', 'updated_at'],
                    row
                ))
                project = projects_map.get(task_dict.get('project_id'))
                task = Task.from_db(task_dict, project)
                tasks_map[task.task_id] = task
            
            # Create agents list with task and project info
            agents = []
            for row in agent_rows:
                db_record = dict(zip(
                    ['id', 'name', 'pixel_character', 'avatar_url', 'role', 'status', 
                     'current_task_id', 'project_id', 'project_name', 'project_url',
                     'created_at', 'updated_at'],
                    row
                ))
                
                task = tasks_map.get(db_record.get('current_task_id'))
                project = projects_map.get(db_record.get('project_id'))
                
                agent = Agent.from_db(db_record, task, project)
                agents.append(agent)
            
            return agents
            
        finally:
            conn.close()
