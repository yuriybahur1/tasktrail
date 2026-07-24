from tasktrail.models import Project


def project_line(project: Project) -> str:
    return (
        f"project id={project.id} "
        f"name={project.name!r} "
        f"status={project.status} "
        f"description={project.description or '-'}"
    )
