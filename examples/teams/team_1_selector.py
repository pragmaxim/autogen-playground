import asyncio
import os
from typing import Sequence
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core import CancellationToken

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Define a model client. You can use other model client that implements the `ChatCompletionClient` interface.
model_client = OllamaChatCompletionClient(
    model="mistral:7b-instruct",
    host=ollama_url
)

async def main() -> None:
    def check_calculation(x: int, y: int, answer: int) -> str:
        if x + y == answer:
            return "Correct!"
        else:
            return "Incorrect!"

    agent1 = AssistantAgent(
        "Agent1",
        model_client,
        description="For calculation",
        system_message="Calculate the sum of two numbers",
    )
    agent2 = AssistantAgent(
        "Agent2",
        model_client,
        tools=[check_calculation],
        description="For checking calculation",
        system_message="Check the answer and respond with 'Correct!' or 'Incorrect!'",
    )

    def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        if len(messages) == 1 or messages[-1].to_text() == "Incorrect!":
            return "Agent1"
        if messages[-1].source == "Agent1":
            return "Agent2"
        return None

    termination = TextMentionTermination("Correct!")
    team = SelectorGroupChat(
        [agent1, agent2],
        model_client=model_client,
        selector_func=selector_func,
        termination_condition=termination,
    )

    await Console(team.run_stream(task="What is 1 + 1?"))

if __name__ == "__main__":
    asyncio.run(main())
