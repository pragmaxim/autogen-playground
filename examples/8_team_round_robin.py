import asyncio
import os
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Define a model client. You can use other model client that implements
# the `ChatCompletionClient` interface.
model_client = OllamaChatCompletionClient(
    model="mistral:7b-instruct",
    host=ollama_url
)

# Create the primary agent.
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a poet.",
)

# Create the green recognition agent.
recognition_agent_green = AssistantAgent(
    "recognition_green",
    model_client=model_client,
    system_message="You are a recognition agent that prints only the word 'green MATCH' if given poem contains the word green or 'GO ON' otherwise.",
)

# Create the tree recognition agent.
recognition_agent_tree = AssistantAgent(
    "recognition_tree",
    model_client=model_client,
    system_message="You are a recognition agent that prints only the word 'tree MATCH' if given poem contains the word tree or 'GO ON' otherwise.",
)

# Define a termination condition that stops the task if the recognition passes.
text_termination = TextMentionTermination("MATCH")

# Create a team with the primary and recognition agents.
team = RoundRobinGroupChat([primary_agent, recognition_agent_green, recognition_agent_tree], termination_condition=text_termination)


async def main() -> None:

    async for message in team.run_stream(task="Write max 64 characters long poem about nature"):  # type: ignore
        if isinstance(message, TaskResult):
            print("Stop Reason:", message.stop_reason)
        else:
            print(message)

if __name__ == "__main__":
    asyncio.run(main())
