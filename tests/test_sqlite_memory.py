from pathlib import Path

from agent_foundry.storage.sqlite import SQLiteSessionStore


def test_saves_and_loads_recent_session_messages(tmp_path: Path) -> None:
    store = SQLiteSessionStore(tmp_path / "memory.sqlite")
    for index in range(3):
        store.save_message(
            project_id="project",
            agent_id="agent",
            session_id="session",
            user_id="user",
            role="user",
            content=f"message-{index}",
        )

    messages = store.load_recent_messages(
        project_id="project",
        agent_id="agent",
        session_id="session",
        user_id="user",
        limit=2,
    )

    assert [message.content for message in messages] == ["message-1", "message-2"]


def test_sessions_are_separated_by_scope(tmp_path: Path) -> None:
    store = SQLiteSessionStore(tmp_path / "memory.sqlite")
    store.save_message(
        project_id="project",
        agent_id="agent",
        session_id="one",
        user_id="user",
        role="user",
        content="session one",
    )
    store.save_message(
        project_id="project",
        agent_id="agent",
        session_id="two",
        user_id="user",
        role="user",
        content="session two",
    )

    messages = store.load_recent_messages(
        project_id="project",
        agent_id="agent",
        session_id="one",
        user_id="user",
        limit=10,
    )

    assert [message.content for message in messages] == ["session one"]


def test_lists_sessions_and_loads_transcript(tmp_path: Path) -> None:
    store = SQLiteSessionStore(tmp_path / "memory.sqlite")
    store.save_message(
        project_id="project",
        agent_id="agent",
        session_id="session",
        user_id="user",
        role="user",
        content="hello",
        context_capsule_id="capsule",
    )
    store.save_message(
        project_id="project",
        agent_id="agent",
        session_id="session",
        user_id="user",
        role="assistant",
        content="hi",
        context_capsule_id="capsule",
    )

    sessions = store.list_sessions(project_id="project")
    messages = store.load_session_messages(session_id="session", project_id="project")

    assert len(sessions) == 1
    assert sessions[0].message_count == 2
    assert [message.content for message in messages] == ["hello", "hi"]
    assert messages[0].context_capsule_id == "capsule"
