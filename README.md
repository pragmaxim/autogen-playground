## AutoGen tutorial with local Ollama models

If you have [ollama](https://ollama.com/) running, these examples should work out of the box on unix systems (Linux, macOS).

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U uv aiofiles autogen-agentchat "autogen-ext[magentic-one,ollama,docker,mcp,web-surfer]"
export OLLAMA_API_BASE=http://localhost:11434
```

### Models

```bash
ollama pull mistral:7b-instruct
# ollama pull mistral-small3.1 # I was able to websurf with this model
```

The model must have tooling capability (and vision for web surfing). 
> Note that unless the Ollama models are listed [here](https://github.com/microsoft/autogen/blob/main/python/packages/autogen-ext/src/autogen_ext/models/ollama/_model_info.py)
> I need to provide `model_info` to the `OllamaChatCompletionClient` constructor.

If you are in doubt which models support function calling and vision, you can check it with these scripts that scan all your local Ollama models :
```bash
./scripts/ollama-tooling-support.sh
./scripts/ollama-vision-support.sh /path/to/an/image.jpg
```

### Rationale

After grasping these examples, we should be able to build a small team of agents like architect, developer and tester
who build a project together until it compiles and all tests pass.

### Examples

***[Chat Completion Client](examples/0_chat_completion_client.py)***

The simplest form of using autogen is just sending a message to the LLM and getting a response back.

***[Assistant Agent](examples/agents/agent_0_assistant.py)***

Assistant agent is a customizable wrapper around the LLM that can be given context, 
handle structured and streaming responses, call functions, interact with other agents in teams, and more.

***[Code Executor Agent](examples/agents/agent_1_code_executor.py)***

This agent was designed to execute code either in local (`LocalCommandLineCodeExecutor`) or 
isolated `DockerCommandLineCodeExecutor` environments.

***[Web Surfer Agent](examples/agents/agent_2_web_surfer.py)***

MultimodalWebSurfer is a multimodal agent that acts as a web surfer that can search the web and visit web pages.

***[Custom agent](examples/agents/agent_3_custom.py)***

Custom made agent that writes given code to a named file.

***[Streaming tokens](examples/1_streaming_tokens.py)***

Token streaming is useful for applications that require real-time interaction with the LLM, such as chatbots.

***[Structured Response](examples/2_structured_response.py)***

Structured responses allow you to define a schema for the responses which can be useful for tasks like classification or structured data extraction.

***[Function Calling](examples/3_function_calling.py)***

- `AssistantAgent` sends request to LLM with function/tool definition
- LLM returns `function_call` (structured tool request)
    ```
    {
      "tool_call": {
        "name": "get_weather",
        "arguments": {"city": "Paris"}
      }
    }
    ```
- `AssistantAgent` handles `function_call`:
     - Calls the corresponding local Python function
     - Feeds function result back to LLM
- LLM produces final answer

***[MCP Server](examples/4_mcp_server.py)***

1. `AssistantAgent` sends the prompt to LLM with tool metadata (JSON schema, tool name, etc.).

2. If the LLM supports function calling, it responds with a `tool_call`.

3. `AssistantAgent` routes the call to `McpWorkbench` which calls `mcp-server-fetch` tool.

4. The `mcp-server-fetch` tool does the fetch (like downloading the Wikipedia page) and returns the result.

5. `AssistantAgent` continues reasoning or summarizing with the result.

***[Team with Round Robin](examples/teams/team_0_round_robin.py)***

Team of agents sharing the same context where each agent takes turn and broadcasts response to the rest of the team.

***[Team with Selector](examples/teams/team_1_selector.py)***

Team of agents that selects the next speaker with a selector function.

***[Human in the Loop](examples/5_human_in_the_loop.py)***

One of the team agents is a `UserProxyAgent` which provides input from the user.

***[Termination](examples/6_termination.py)***

- `MaxMessageTermination`: Stops after a specified number of messages have been produced, including both agent and task messages.
- `TextMentionTermination`: Stops when specific text or string is mentioned in a message (e.g., “TERMINATE”).
- `TokenUsageTermination`: Stops when a certain number of prompt or completion tokens are used. This requires the agents to report token usage in their messages.
- `TimeoutTermination`: Stops after a specified duration in seconds.
- `HandoffTermination`: Stops when a handoff to a specific target is requested to allow another agent to provide input.
- `SourceMatchTermination`: Stops after a specific agent responds.
- `ExternalTermination`: Enables programmatic control of termination from outside the run. This is useful for UI integration (e.g., “Stop” buttons in chat interfaces).
- `StopMessageTermination`: Stops when a StopMessage is produced by an agent.
- `TextMessageTermination`: Stops when a TextMessage is produced by an agent.
- `FunctionCallTermination`: Stops when a ToolCallExecutionEvent containing a FunctionExecutionResult with a matching name is produced by an agent.
- `FunctionalTermination`: Stop when a function expression is evaluated to True on the last delta sequence of messages.

***[Saving](examples/state/state_0_saving.py) and [Loading](examples/state/state_1_loading.py) State***

Agent and Team interfaces have `save_state` and `load_state` methods to either a file or a database.

### Troubleshooting

1. Note that advanced agents with deep reasoning or large context should use large `70B` models on a GPU with at least 48GB of VRAM
   like `NVIDIA Quadro RTX 8000 48GB`. I tend to prototype with local models through [ollama](https://ollama.com/) or
   [llama-cpp](https://github.com/ggml-org/llama.cpp) server because the `openAI` bill can be quite high, especially with `GPT-4o` models.

2. Be sure that Ollama is really using underlying GPU like nvidia with cuda toolkit compiled, otherwise it will be very slow.
3. Increase `OLLAMA_CONTEXT_LENGTH=` in case the context of your agent team grows.
