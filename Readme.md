# Taskpaper CLI

This is still very early stages, but offers the ability to

- add projects at the top level
- add projects at the project level
- add tasks at the project level
- complete tasks
- find projects by name and return a project object containing a list of task objects 

## Initializing

	from taskpaper import TaskPaper
	
	my_file = '/some/path/tasks.taskpaper'
	
	t = TaskPaper(my_file)

## Projects

	all_projects = t.projects

	new_project = t.create_project("My New Project")
	
	cycling = all_projects.get_by_name('Cycling')
	
	training = cycling.add_subproject('Training')
	
	print cycling.name # Cycling

## Tasks

	all_tasks = cycling.tasks
	
	print "\n".join([task.task for task in all_tasks])
	
	new_task = cycling.add_task('go ride my bike')
	
	new_subtask = training.add_task('lunges')
	
	new_task.complete()

## Todo

- needs refactoring
- write tests
- read due dates for tasks if they exist
- add tags to tasks when creating tasks
- set due dates for tasks
- returning subprojects fails if you get the subprojects at the very bottom of a list
