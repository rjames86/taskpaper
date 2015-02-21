# Taskpaper CLI

## Initializing

```python
	from taskpaper import TaskPaper
	
	my_file = '/some/path/tasks.taskpaper'
	
	t = TaskPaper(my_file)
```

## Projects

```python
	# Get all projects
	all_projects = t.projects

	# Create a new top-level project
	new_project = t.create_project("My New Project")

	# Get a project by name
	cycling = all_projects.get_by_name('Cycling')

	# Create a subproject
	training = cycling.add_subproject('Training')

	# Print name of the task
	print cycling.name # Cycling
```

## Tasks

```python
	# Get all tasks within a project
	all_tasks = cycling.tasks
	
	# Create a new task within a project
	new_task = cycling.add_task('go ride my bike')

	# Create tasks with tags
	new_tagged_task = cycling.add_task(
		'learn to change disc brake pads',
		tags=['@people(joe)', 'tomorrow'] # the @ will be added if you leave it out
	)
	
	# Create a subtask
	new_subtask = training.add_task('lunges')
	
	# Complete a task
	new_task.complete()
```

## Todo

- write tests
- read due dates for tasks if they exist
