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
                trailing_newline=False),
            position)
        self._write_to_project()
        return project

    def _get_projects(self, content=None):
        to_ret = Projects()
        if not content:
            content = self.raw_content
        re_project = re.compile(
            r'(?P<indent>^|\s{2,}|\t+)(?P<project>[\w ]+):(?:\s+|$)', re.UNICODE)
        for index, line in enumerate(content.splitlines()):
            project_search = re_project.search(line)
            if project_search:
                indent_level = len(project_search.group("indent"))
                to_ret.append(
                    Project(self,
                            project_search.group("project"),
                            indent_level))
        return to_ret

    def _get_raw_content(self, is_string):
        if is_string:
            self.is_string = True
            return self.filename
        with open(self.filename, 'r') as f:
            return f.read()

    def _insert_in_project(self,
                           content,
                           position=0,
                           end=False,
                           trailing_newline=True):
        end = end if end else position
        self.raw_content = \
            self.raw_content[:position] + \
            content + ("\n" if trailing_newline else '') + \
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
        self._tp = tp
        self.name = name
        self.tags = []
        self._tasks = Tasks(self)
        self.indent_level = indent_level

    def __repr__(self):
        return "<Project %s>" % self.name

    @property
    def raw_content(self):
        return self._tp.raw_content[
            self._project_index: self._next_project_index]

    @property
    def tasks(self):
        if not self._tasks:
            self._tasks.get_tasks()
        return self._tasks

    @property
    def subprojects(self):
        return self._get_subprojects()

    @property
    def _project_index(self):
        return self._tp._get_text_position("{}:".format(self.name))

    @property
    def _next_newline(self):
        """get the position of the next newline after the project"""
        return self._project_index + \
            self._tp._get_text_position("\n", self._project_index)

    @property
    def _next_project_index(self):
        return self._check_for_endproject()

    def add_task(self, task, tags=[], notes=""):
        new_task = Task(task, self, tags=tags, notes=notes)
        self._tp._insert_in_project(
            new_task.toString(),
            self._get_position()
        )
        self._tp._write_to_project()
        self._tasks.append(new_task)
        return new_task

    def add_subproject(self, project_name):
        """creates a subproject at the very bottom of the project"""
        return self._tp.create_project(
            project_name,
            self.indent_level + 1,
            self._next_project_index - 1,
            extra_newline=False
        )

    def _get_subprojects(self):
        """get subprojects for a given project. It first checks the list of
        (indent, indexes) to see if the next project is 0, which means the
        current project is at the very end"""
        next_project_index = self._check_for_endproject()
        content = \
            self._tp.raw_content[self._next_newline: next_project_index]
        return self._tp._get_projects(content)

    def _check_for_endproject(self):
        check_index = self._tp.projects._get_indent_indexes(self._project_index)
        for indent, index in check_index[1:]:
            if indent == 0:
                return index
        return self._next_project_index

    def _get_position(self):
        return self._next_newline + 1


class Projects(list):
    def get_by_name(self, name):
        for project in self:
            if project.name == name:
                return project

    def _get_all_indexes(self, indent_level=-1):
        return sorted(set([p._project_index for p in self
                      if p.indent_level == indent_level])) \
            if indent_level >= 0 \
            else [p._project_index for p in self]

    def _get_all_indents(self):
        return [p.indent_level for p in self]

    def _get_indent_indexes(self, start=0):
        """returns tuple of (index level, position) starting at
        a given position in the raw_content"""
        all_indexes = self._get_all_indexes()
        index = all_indexes.index(start)
        return zip(self._get_all_indents()[index:], all_indexes[index:])


class Task(object):
    def __init__(self, task, project, *args, **kwargs):
        tags = kwargs['tags'] if kwargs.get('tags') else None
        notes = kwargs['notes'] if kwargs.get('notes') else None

        self.project = project
        self.task = task
        self.tags = self._set_tags(tags) if tags else []
        self.notes = notes if notes else ""

    def __str__(self):
        return "{tabs}- {task}{tags}{notes}".format(
            tabs="\t" * (self.project.indent_level + 1),
            task=self.task,
            tags=self._get_tag_string(),
            notes=self._get_notes_string()
            )

    def toString(self):
        return self.__str__()

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
        start_index = self.project._tp._get_text_position(original_task)
        end_index = start_index + len(original_task)
        self.project._tp._insert_in_project(
            self.task,
            start_index,
            end_index,
            trailing_newline=False
        )
        self.project._tp._write_to_project()

    def __repr__(self):
        return "<Task Item>"

    def _set_tags(self, tags):
        if isinstance(tags, str):
            tags = [tags]
        tags = map(self._add_arroba, tags)
        return tags

    def _add_arroba(self, tag):
        return '@' + tag if not tag.startswith('@') else tag

    def _get_tag_string(self):
        return " " + " ".join(self.tags)

    def _get_notes_string(self):
        return "".join(
            "{tabs}{note}\n".format(
                tabs="\t" * (self.project.indent_level + 2),
                note=note)
            for note in self.notes.split('\n')
            )


class Tasks(list):
    def __init__(self, project):
        self.raw_content = project._tp.raw_content
        self.project = project

    def get_tasks(self):
        all_tasks = self._get_all_tasks()
        for task in all_tasks:
            tags = self._get_tags_from_task(task)
            clean_task = self._cleanup_task(task, tags)
            self.append(
                Task(clean_task, self.project, tags=tags)
            )

    @property
    def todays_tasks(self):
        return [task for task in self
                if '@today' in task.tags and
                '@done' not in task.tags]

    def _get_all_tasks(self):
        re_search = re.compile(r'\n\t{%s}-(?:\s|\t)(.*)(?:(?=@)|(?=\n))' %
                               (self.project.indent_level + 1), re.UNICODE)
        start = self.project._get_position() - 1
        end = self.project._next_project_index
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
