import asyncio
import json
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Define a model client. You can use other model client that implements the `ChatCompletionClient` interface.
model_client = OllamaChatCompletionClient(
    model="mistral:7b-instruct",
    host=ollama_url
)

# Run the agent and stream the messages to the console.
async def main() -> None:
    new_assistant_agent = AssistantAgent(
        name="assistant_agent",
        system_message="You are a helpful assistant",
        model_client=model_client,
    )

    with open("out/agent_state.json", "r") as f:
        agent_state = json.load(f)

    await new_assistant_agent.load_state(agent_state)

    # Use asyncio.run(...) when running in a script.
    response = await new_assistant_agent.on_messages(
        [TextMessage(content="What was the last line of the previous poem you wrote", source="user")], CancellationToken()
    )
    print(response.chat_message)
    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())
