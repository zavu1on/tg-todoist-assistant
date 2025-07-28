from datetime import date, timedelta

from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.models import Task


class Todoist:

    def get_api_client(self, token: str) -> TodoistAPIAsync:
        return TodoistAPIAsync(token)

    async def create_task(self, token: str, task_config: dict) -> Task:
        """Create a new task in Todoist

        Args:
            token: The access token for the Todoist API
            task_config: A dictionary with the following fields:
                content: The name of the task
                description: A description of the task (optional)
                priority: The priority of the task (1-4) (optional)
                due_datetime: The due datetime of the task in ISO 8601 format (optional)

        Returns:
            A Task object with the ID of the newly created task
        """

        client = self.get_api_client(token)
        return await client.add_task(**task_config)

    async def get_daily_tasks(self, token: str) -> list[Task]:
        client = self.get_api_client(token)
        all_tasks = await client.get_tasks()
        today = date.today()

        daily_tasks = []
        async for task_list in all_tasks:
            for task in task_list:
                if task.due:
                    task_due_date = date(
                        task.due.date.year,
                        task.due.date.month,
                        task.due.date.day,
                    )
                    if task_due_date == today:
                        daily_tasks.append(task)

        return daily_tasks

    async def get_weekly_tasks(self, token: str) -> list[Task]:
        client = self.get_api_client(token)
        all_tasks = await client.get_tasks()

        start_day = date.today()
        end_day = start_day + timedelta(days=7)

        weekly_tasks = []
        async for task_list in all_tasks:
            for task in task_list:
                if task.due:
                    task_due_date = date(
                        task.due.date.year,
                        task.due.date.month,
                        task.due.date.day,
                    )
                    if start_day <= task_due_date <= end_day:
                        weekly_tasks.append(task)

        return weekly_tasks

    async def delete_task(self, token: str, task_id: int) -> bool:
        client = self.get_api_client(token)
        return await client.delete_task(task_id)


todoist = Todoist()
