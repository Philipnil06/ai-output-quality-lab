from dataclasses import dataclass


@dataclass
class CaseConfig:
    name: str
    task: str
    audience: str
    tone: str
    constraints: dict
    keywords_file: str


@dataclass
class PromptVariant:
    name: str
    system_prompt: str
    user_prompt_template: str


def render_user_prompt(template: str, case: CaseConfig) -> str:
    return template.format(
        name=case.name,
        task=case.task,
        audience=case.audience,
        tone=case.tone,
        constraints=case.constraints,
    )

