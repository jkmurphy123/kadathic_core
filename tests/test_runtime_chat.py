from agent_foundry import AgentRuntime, AppContext, ChatRequest, ChatResponse


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


def test_runtime_chat_with_mock_provider() -> None:
    runtime = AgentRuntime.from_project_config("examples/sample_project/agentfoundry.yaml")

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
