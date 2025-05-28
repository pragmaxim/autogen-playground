import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Get the fetch tool from mcp-server-fetch.
fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])

model_client = OllamaChatCompletionClient(
    model="mistral:7b-instruct",
    host=ollama_url
)

# Run the agent and stream the messages to the console.
async def main() -> None:
# Create an MCP workbench which provides a session to the mcp server.
    async with McpWorkbench(fetch_mcp_server) as workbench:  # type: ignore
        # Create an agent that can use the fetch tool.
        fetch_agent = AssistantAgent(
            name="fetcher", model_client=model_client, workbench=workbench, reflect_on_tool_use=True
        )

        # Let the agent fetch the content of a URL and summarize it.
        result = await fetch_agent.run(task="Summarize the content of https://en.wikipedia.org/wiki/Seattle")
        assert isinstance(result.messages[-1], TextMessage)
        print(result.messages[-1].content)

        # Close the connection to the model client.
        await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())
