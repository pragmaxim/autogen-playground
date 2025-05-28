import asyncio
import os
from autogen_agentchat.ui import Console
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_agentchat.conditions import TextMessageTermination

ollama_url = os.environ.get("OLLAMA_API_BASE")

# Define a model client. You can use other model client that implements the `ChatCompletionClient` interface.
model_client = OllamaChatCompletionClient(
    model="mistral:7b-instruct",
    host=ollama_url
)

termination_condition = TextMessageTermination("code_executor_agent")


async def main() -> None:
    # define the Docker CLI Code Executor
    code_executor = DockerCommandLineCodeExecutor(work_dir="coding")

    # start the execution container
    await code_executor.start()

    code_executor_agent = CodeExecutorAgent(
        "code_executor_agent", code_executor=code_executor, model_client=model_client
    )

    task = "Write python code to print Hello World!"
    await Console(code_executor_agent.run_stream(task=task))

    # stop the execution container
    await code_executor.stop()

if __name__ == "__main__":
    asyncio.run(main())
