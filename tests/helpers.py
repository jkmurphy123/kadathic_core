from pathlib import Path


def write_temp_project_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "agentfoundry.yaml"
    agents_path = (Path("examples") / "agents").resolve().as_posix()
    storage_path = (tmp_path / "agent_foundry.sqlite").as_posix()
    config_path.write_text(
        f"""
project:
  id: demo_project
  name: Demo Project

default_provider: mock

providers:
  mock:
    type: mock
    model: mock-model

agent_libraries:
  - {agents_path}

enabled_agents:
  - chat_companion
  - quiz_tutor
  - game_companion

storage:
  path: {storage_path}

context_policy:
  include_app_context: true
  max_recent_messages: 12
  app_context_position: before_user_message
""".strip(),
        encoding="utf-8",
    )
    return config_path
