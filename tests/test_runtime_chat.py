from pathlib import Path

from agent_foundry import AgentRuntime, AppContext, ChatRequest, ChatResponse
from agent_foundry.storage.sqlite import SQLiteSessionStore
from tests.helpers import write_temp_project_config


def test_public_runtime_imports_are_available() -> None:
    request = ChatRequest(
        agent_id="chat_companion",
        project_id="demo_project",
        session_id="session-001",
        user_id="local-user",
        user_message="Hello",
    )

    assert request.agent_id == "chat_companion"
    assert ChatResponse
    assert AgentRuntime
    assert AppContext


def test_runtime_chat_with_mock_provider(tmp_path: Path) -> None:
    config_path = write_temp_project_config(tmp_path)
    runtime = AgentRuntime.from_project_config(config_path)

    response = runtime.chat(
        agent_id="quiz_tutor",
        project_id="demo_project",
        session_id="session-001",
        user_id="local-user",
        user_message="Can I get a hint?",
        app_context=AppContext.simple(
            app_id="quiz",
            app_type="quiz",
            state_summary="Question 1 is visible.",
        ),
    )

    assert response.text == "[mock:mock] Can I get a hint?"
    assert response.agent_id == "quiz_tutor"
    assert response.session_id == "session-001"
    assert response.provider_id == "mock"
    assert response.model == "mock-model"
    assert response.context_capsule_id
    assert response.metadata["message_count"] == 2
    assert response.metadata["project_id"] == "demo_project"


def test_runtime_chat_saves_and_loads_recent_messages(tmp_path: Path) -> None:
    config_path = write_temp_project_config(tmp_path)
    runtime = AgentRuntime.from_project_config(config_path)

    first_response = runtime.chat(
        agent_id="quiz_tutor",
        project_id="demo_project",
        session_id="session-001",
        user_id="local-user",
        user_message="First message",
        app_context=AppContext.simple(
            app_id="quiz",
            app_type="quiz",
            state_summary="Question 1 is visible.",
        ),
    )
    second_response = runtime.chat(
        agent_id="quiz_tutor",
        project_id="demo_project",
        session_id="session-001",
        user_id="local-user",
        user_message="Second message",
        app_context=AppContext.simple(
            app_id="quiz",
            app_type="quiz",
            state_summary="Question 1 is still visible.",
        ),
    )

    store = SQLiteSessionStore(tmp_path / "agent_foundry.sqlite")
    messages = store.load_session_messages(session_id="session-001", project_id="demo_project")

    assert first_response.metadata["message_count"] == 2
    assert second_response.metadata["message_count"] == 4
    assert [message.role for message in messages] == ["user", "assistant", "user", "assistant"]


def test_runtime_uses_project_default_provider_when_agent_has_no_override(tmp_path: Path) -> None:
    config_path = write_temp_project_config(tmp_path)
    config_text = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        config_text.replace("default_provider: mock", "default_provider: alt_mock").replace(
            "    model: mock-model",
            """
    model: mock-model

  alt_mock:
    type: mock
    model: alternate-mock-model
""".rstrip(),
        ),
        encoding="utf-8",
    )

    runtime = AgentRuntime.from_project_config(config_path)

    response = runtime.chat(
        agent_id="chat_companion",
        project_id="demo_project",
        session_id="session-001",
        user_id="local-user",
        user_message="Hello",
    )

    assert response.provider_id == "alt_mock"
    assert response.model == "alternate-mock-model"
