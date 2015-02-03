import re


class Base(object):
    def create_project(self,
                       project_name,
                       indent_level=0,
                       position=0,
                       extra_newline=False):
        project = Project(self, project_name, indent_level)
        self._insert_in_project(
            "{}{}{}:".format(
                '\n' if extra_newline else '',
                "\t" * indent_level,
                project_name,
                False),
            position)
        self._write_to_project()
        return project

    def _insert_in_project(self, content, position=0, trailing_newline=True):
        self.raw_content = \
            self.raw_content[:position] + \
            content + ("\n" if trailing_newline else '') + \
            self.raw_content[position:]

    def _replace_in_project(self, content, start, end):
        self.raw_content = \
            self.raw_content[:start] + \
            content + \
            self.raw_content[end:]

    def _write_to_project(self):
        if hasattr(self, 'is_string'):
            return
        with open(self.filename, 'w') as f:
            f.write(self.raw_content)

    def _get_text_position(self, query, from_position=0):
        return self.raw_content[from_position:].find(query)


class Project(object):
    def __init__(self, tp, name, indent_level=0):
        self.tp = tp
        self.name = name
        self.tags = []
        self._tasks = Tasks(self)
        self.indent_level = indent_level

    @property
    def raw_content(self):
        return self.tp.raw_content[self.project_index: self.next_project_index]

    @property
    def tasks(self):
        if not self._tasks:
            self._tasks.get_tasks()
        return self._tasks

    @property
    def project_index(self):
        return self.tp._get_text_position("{}:".format(self.name))

    @property
    def next_newline(self):
        """get the position of the next newline after the project"""
        return self.project_index + \
            self.tp._get_text_position("\n", self.project_index)

    @property
    def next_project_index(self):
        """
        Looks for the next position in the raw content for a
        project at the same indent level
        """
        indexes = self.tp.projects.get_all_indexes(self.indent_level)
        try:
            return indexes[indexes.index(self.project_index) + 1]
        except IndexError:
            return len(self.tp.raw_content)

    @property
    def subprojects(self):
        return self._get_subprojects()

    def __repr__(self):
        return "<Project %s>" % self.name

    def add_subproject(self, project_name):
        """creates a subproject at the very bottom of the project"""
        return self.tp.create_project(
            project_name,
            self.indent_level + 1,
            self.next_project_index - 1,
            extra_newline=False
        )

    def _get_subprojects(self):
        content = \
            self.tp.raw_content[self.next_newline: self.next_project_index]
        return self.tp._get_projects(content)

    def add_task(self, task, tags=[], notes=""):
        new_task = Task(task, self, tags=tags, notes=notes)
        self.tp._insert_in_project(
            "{}- {}".format("\t" * (self.indent_level + 1), new_task.task),
            self._get_position()
        )
        self.tp._write_to_project()
        self._tasks.append(new_task)
        return new_task

    def _get_position(self):
        return self.next_newline + 1


class Projects(list):
    def get_by_name(self, name):
        for project in self:
            if project.name == name:
                return project

    def get_all_indexes(self, indent_level):
        return sorted(set([p.project_index
                      for p in self
                      if p.indent_level == indent_level]))


class Task(object):
    def __init__(self, task, project, *args, **kwargs):
        tags = kwargs['tags'] if kwargs.get('tags') else None
        notes = kwargs['notes'] if kwargs.get('notes') else None

        self.project = project
        self.task = task
        self.tags = self._set_tags(tags) if tags else []
        self.notes = notes if notes else ""

    def complete(self):
        from datetime import datetime
        tag_template = "@{name}({tag})"
        now_tag = tag_template.format(
            name="done",
            tag=datetime.now().strftime("%Y-%m-%d %H:%M"))
        project_tag = tag_template.format(
            name="project",
            tag=self.project.name)

        original_task = self.task
        self.task = self.task + " {} {}".format(
            now_tag,
            project_tag
        )
        start_index = self.project.tp._get_text_position(original_task)
        end_index = start_index + len(original_task)
        self.project.tp._replace_in_project(
            self.task,
            start_index,
            end_index
        )
        self.project.tp._write_to_project()

    def __repr__(self):
        return "<Task Item>"

    def _set_tags(self, tags):
        if isinstance(tags, str):
            tags = [tags]
        return tags


class Tasks(list):
    def __init__(self, project):
        self.raw_content = project.tp.raw_content
        self.project = project

    def get_tasks(self):
        all_tasks = self._get_all_tasks()
        for task in all_tasks:
            tags = self._get_tags_from_task(task)
            clean_task = self._cleanup_task(task, tags)
            self.append(
                Task(clean_task, self.project, tags=tags)
            )

    def _get_all_tasks(self):
        re_search = re.compile(r'\n\t{%s}-(?:\s|\t)(.*)(?:(?=@)|(?=\n))' %
                               (self.project.indent_level + 1), re.UNICODE)
        start = self.project._get_position() - 1
        end = self.project.next_project_index
        return re_search.findall(
            self.raw_content[start:end])

    def _get_tags_from_task(self, task):
        """looks for @tag or @tag(things)"""
        re_search = re.compile(r'@\w+(?:\(.*\))?')
        return re_search.findall(task)

    def _cleanup_task(self, task, tags):
        to_remove = r"|".join(
            [tag.replace('(', '\(').replace(')', '\)')
                for tag in tags])
        return re.sub(to_remove, '', task).strip()


class TaskPaper(Base):
    def __init__(self, filename, is_string=False):
        self.filename = filename
        self.raw_content = self._get_raw_content(is_string)

    @property
    def projects(self):
        return self._get_projects()

    def _get_raw_content(self, is_string):
        if is_string:
            self.is_string = True
            return self.filename
        with open(self.filename, 'r') as f:
            return f.read()
