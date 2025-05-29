import asyncio
import os
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Create the agents.
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
    system_message="You are a recognition agent matching word 'green' in which cases returns 'green MATCH', otherwise returns 'GO ON'.",
)

# Create the tree recognition agent.
recognition_agent_tree = AssistantAgent(
    "recognition_tree",
    model_client=model_client,
    system_message="You are a recognition agent matching word 'tree' in which cases returns 'tree MATCH', otherwise returns 'GO ON'.",
)

async def main() -> None:
    max_msg_termination = MaxMessageTermination(max_messages=10)
    text_termination = TextMentionTermination("MATCH")
    # Create a team with the primary and recognition agents.
    combined_termination = max_msg_termination | text_termination

    round_robin_team = RoundRobinGroupChat([primary_agent, recognition_agent_green, recognition_agent_tree], termination_condition=combined_termination)

    # Use asyncio.run(...) if you are running this script as a standalone script.
    await Console(round_robin_team.run_stream(task="Write max 64 characters long poem about nature"))

    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())
