import asyncio
import os
from autogen_agentchat.ui import Console
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import ModelInfo
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

ollama_url = os.environ.get("OLLAMA_API_BASE")

model_info = ModelInfo(
    id="mistral-small3.1",
    name="mistral-small3.1",
    provider="ollama",
    version="latest",
    json_output=True,
    function_calling=True,
    family="mistral",
    vision=True,
)

# Define a model client. You can use other model client that implements the `ChatCompletionClient` interface.
model_client = OllamaChatCompletionClient(
    model="mistral-small3.1",
    host=ollama_url,
    model_info=model_info,
)

async def main() -> None:
    # Define an agent
    web_surfer_agent = MultimodalWebSurfer(
        name="MultimodalWebSurfer",
        model_client=model_client,
    )

    # Define a team
    agent_team = RoundRobinGroupChat([web_surfer_agent], max_turns=3)

    # Run the team and stream messages to the console
    stream = agent_team.run_stream(task="Navigate to the AutoGen readme on GitHub.")
    await Console(stream)
    # Close the browser controlled by the agent
    await web_surfer_agent.close()


asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
