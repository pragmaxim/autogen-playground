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

### Examples

***[Chat Completion Client](examples/0_chat_completion_client.py)***

The simplest form of using autogen is just sending a message to the LLM and getting a response back.

***[Assistant Agent](examples/1_assistant_agent.py)***

Assistant agent is a customizable wrapper around the LLM that can be given context, 
handle structured and streaming responses, call functions, interact with other agents in teams, and more.

***[Code Executor Agent](examples/2_code_executor_agent.py)***

This agent was designed to execute code either in local (`LocalCommandLineCodeExecutor`) or 
isolated `DockerCommandLineCodeExecutor` environments.

***[Web Surfer Agent](examples/3_web_surfer_agent.py)***

MultimodalWebSurfer is a multimodal agent that acts as a web surfer that can search the web and visit web pages.

***[Streaming tokens](examples/4_streaming_tokens.py)***

Token streaming is useful for applications that require real-time interaction with the LLM, such as chatbots.

***[Structured Response](examples/5_structured_response.py)***

Structured responses allow you to define a schema for the responses which can be useful for tasks like classification or structured data extraction.

***[Function Calling](examples/6_function_calling.py)***

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

***[MCP Server](examples/7_mcp_server.py)***

1. `AssistantAgent` sends the prompt to LLM with tool metadata (JSON schema, tool name, etc.).

2. If the LLM supports function calling, it responds with a `tool_call`.

3. `AssistantAgent` routes the call to `McpWorkbench` which calls `mcp-server-fetch` tool.

4. The `mcp-server-fetch` tool does the fetch (like downloading the Wikipedia page) and returns the result.

5. `AssistantAgent` continues reasoning or summarizing with the result.

***[Team with Round Robin](examples/8_team_round_robin.py)***

Team of agents sharing the same context where each agent takes turn and broadcasts response to the rest of the team.

***[Team with Selector](examples/9_team_selector.py)***

Team of agents that selects the next speaker with a selector function.

### Troubleshooting

1. Note that advanced agents with deep reasoning or large context should use large `70B` models on a GPU with at least 48GB of VRAM
   like `NVIDIA Quadro RTX 8000 48GB`. I tend to prototype with local models through [ollama](https://ollama.com/) or
   [llama-cpp](https://github.com/ggml-org/llama.cpp) server because the `openAI` bill can be quite high, especially with `GPT-4o` models.

2. Be sure that Ollama is really using underlying GPU like nvidia with cuda toolkit compiled, otherwise it will be very slow.
3. Increase `OLLAMA_CONTEXT_LENGTH=` in case the context of your agent team grows.
