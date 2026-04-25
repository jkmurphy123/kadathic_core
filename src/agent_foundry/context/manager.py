"""Build context capsules from project, agent, and app inputs."""

from agent_foundry.agents.definition import AgentDefinition
from agent_foundry.config.models import ProjectConfig
from agent_foundry.context.app_context import AppContext
from agent_foundry.context.capsule import ContextCapsule
from agent_foundry.context.policy import ContextPolicy
from agent_foundry.context.renderer import render_app_context
from agent_foundry.providers.base import ProviderMessage

DEFAULT_SYSTEM_INSTRUCTIONS = (
    "You are an AI agent running inside Agent Foundry. Follow the agent personality, "
    "respect project and app context, and treat current app context as authoritative "
    "over stale memory or prior conversation."
)


class ContextManager:
    """Assembles inspectable context capsules for agent turns."""

    def __init__(
        self,
        system_instructions: str = DEFAULT_SYSTEM_INSTRUCTIONS,
    ) -> None:
        self.system_instructions = system_instructions

    def assemble(
        self,
        *,
        project_config: ProjectConfig,
        agent: AgentDefinition,
        project_id: str | None = None,
        session_id: str,
        user_id: str,
        user_message: str,
        app_context: AppContext | None = None,
        recent_messages: list[ProviderMessage] | None = None,
        policy: ContextPolicy | None = None,
    ) -> ContextCapsule:
        """Assemble a `ContextCapsule` for one turn."""

        effective_policy = policy or self._policy_from_config(project_config, agent)
        effective_recent_messages = (recent_messages or [])[
            -effective_policy.max_recent_messages :
        ]
        rendered_messages = self._render_messages(
            agent=agent,
            project_config=project_config,
            user_message=user_message,
            app_context=app_context if effective_policy.include_app_context else None,
            recent_messages=effective_recent_messages,
        )
        effective_project_id = project_id or project_config.project.id

        return ContextCapsule(
            user_id=user_id,
            project_id=effective_project_id,
            agent_id=agent.id,
            session_id=session_id,
            system_instructions=self.system_instructions,
            agent_personality=agent.personality or "",
            project_context=self._render_project_context(project_config),
            recent_messages=effective_recent_messages,
            app_context=app_context if effective_policy.include_app_context else None,
            current_user_message=user_message,
            rendered_messages=rendered_messages,
            metadata={
                "context_policy": effective_policy.model_dump(),
                "configured_project_id": project_config.project.id,
            },
        )

    def _policy_from_config(
        self,
        project_config: ProjectConfig,
        agent: AgentDefinition,
    ) -> ContextPolicy:
        include_app_context = project_config.context_policy.include_app_context
        if agent.context_policy.include_app_context is not None:
            include_app_context = agent.context_policy.include_app_context

        return ContextPolicy(
            include_app_context=include_app_context,
            max_recent_messages=project_config.context_policy.max_recent_messages,
            app_context_position=project_config.context_policy.app_context_position,
        )

    def _render_messages(
        self,
        *,
        agent: AgentDefinition,
        project_config: ProjectConfig,
        user_message: str,
        app_context: AppContext | None,
        recent_messages: list[ProviderMessage],
    ) -> list[ProviderMessage]:
        system_content = "\n\n".join(
            section
            for section in [
                f"## System Instructions\n{self.system_instructions}",
                f"## Agent Personality\n{agent.personality or ''}",
                self._render_project_context(project_config),
            ]
            if section
        )

        user_sections = []
        if app_context is not None:
            user_sections.append(render_app_context(app_context))
        user_sections.append(f"## Current User Message\n{user_message}")

        rendered_messages = [ProviderMessage(role="system", content=system_content)]
        rendered_messages.extend(recent_messages)
        rendered_messages.append(ProviderMessage(role="user", content="\n\n".join(user_sections)))
        return rendered_messages

    def _render_project_context(self, project_config: ProjectConfig) -> str:
        project_name = project_config.project.name or project_config.project.id
        return (
            f"## Project Context\n"
            f"Project: {project_name}\n"
            f"Project ID: {project_config.project.id}"
        )
