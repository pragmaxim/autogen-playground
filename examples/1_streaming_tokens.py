import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.ollama import OllamaChatCompletionClient

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Define a model client. You can use other model client that implements the `ChatCompletionClient` interface.
model_client = OllamaChatCompletionClient(
    model="mistral:7b-instruct",
    host=ollama_url
)

streaming_assistant = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="You are a helpful assistant.",
    model_client_stream=True,  # Enable streaming tokens.
)

# Run the agent and stream the messages to the console.
async def main() -> None:
    async for message in streaming_assistant.run_stream(task="Name two cities in South America"):  # type: ignore
        print(message)

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
