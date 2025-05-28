import asyncio
import os
from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Assuming your Ollama server is running locally on port 11434.
ollama_model_client = OllamaChatCompletionClient(
    model="mistral:7b-instruct",
    host=ollama_url
)

async def main() -> None:
    response = await ollama_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(response)
    await ollama_model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
