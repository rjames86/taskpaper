# Taskpaper CLI

## Initializing

	from taskpaper import TaskPaper
	
	my_file = '/some/path/tasks.taskpaper'
	
	t = TaskPaper(my_file)

## Projects

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

## Tasks

	# Get all tasks within a project
	all_tasks = cycling.tasks
	
	# Create a new task within a project
	new_task = cycling.add_task('go ride my bike')
	
	# Create a subtask
	new_subtask = training.add_task('lunges')
	
	# Complete a task
	new_task.complete()

## Todo

- write tests
- read due dates for tasks if they exist
