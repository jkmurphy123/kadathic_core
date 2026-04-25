from agent_foundry.agents.registry import AgentRegistry
from agent_foundry.config.loader import load_project_config
from agent_foundry.context.app_context import AppContext
from agent_foundry.context.manager import ContextManager


def test_assembles_context_capsule() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")
    agent = AgentRegistry.from_libraries(config.resolved_agent_libraries()).get("quiz_tutor")
    app_context = AppContext.simple(
        app_id="quiz",
        app_type="quiz",
        state_summary="Question 1 is visible.",
    )

    capsule = ContextManager().assemble(
        project_config=config,
        agent=agent,
        session_id="session-001",
        user_id="local-user",
        user_message="Can I get a hint?",
        app_context=app_context,
    )

    assert capsule.id
    assert capsule.project_id == "demo_project"
    assert capsule.agent_id == "quiz_tutor"
    assert capsule.session_id == "session-001"
    assert capsule.user_id == "local-user"
    assert capsule.app_context == app_context
    assert len(capsule.rendered_messages) == 2
    assert capsule.rendered_messages[0].role == "system"
    assert capsule.rendered_messages[1].role == "user"


def test_current_app_context_appears_before_current_user_message() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")
    agent = AgentRegistry.from_libraries(config.resolved_agent_libraries()).get("quiz_tutor")
    app_context = AppContext.simple(
        app_id="quiz",
        app_type="quiz",
        state_summary="The answer is not visible to the player.",
    )

    capsule = ContextManager().assemble(
        project_config=config,
        agent=agent,
        session_id="session-001",
        user_id="local-user",
        user_message="What should I try?",
        app_context=app_context,
    )

    user_content = capsule.rendered_messages[1].content
    assert user_content.index("## Current App Context") < user_content.index(
        "## Current User Message"
    )
    assert "The answer is not visible to the player." in user_content
    assert "What should I try?" in user_content


def test_agent_policy_can_omit_app_context() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")
    agent = AgentRegistry.from_libraries(config.resolved_agent_libraries()).get("chat_companion")
    app_context = AppContext.simple(
        app_id="chat",
        app_type="chatbot",
        state_summary="Should be omitted by agent policy.",
    )

    capsule = ContextManager().assemble(
        project_config=config,
        agent=agent,
        session_id="session-001",
        user_id="local-user",
        user_message="Hello",
        app_context=app_context,
    )

    assert capsule.app_context is None
    assert "Should be omitted" not in capsule.rendered_messages[1].content
