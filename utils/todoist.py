from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.models import Task

# todo
# дела на сегодня
# сделай план из дел на сегодня
# анализ ближайших дел


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
                labels: A list of strings of the labels to add to the task (optional)

        Returns:
            A Task object with the ID of the newly created task
        """

        client = self.get_api_client(token)
        return await client.add_task(**task_config)


todoist = Todoist()
