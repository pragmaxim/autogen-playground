#!/bin/bash

# This script makes a list of locally installed Ollama models and checks if they support tooling.

if [ -z "$OLLAMA_API_BASE" ]; then
  echo "export OLLAMA_API_BASE=http://localhost:11434"
  exit 1
fi

read -r -d '' TOOLS_JSON << EOM
[
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get weather for a city",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {
            "type": "string",
            "description": "City to get weather for"
          }
        },
        "required": ["city"]
      }
    }
  }
]
EOM

# Get list of local models
models=$(ollama ls | awk 'NR>1 {print $1}')

for model in $models; do
  # Send completion request with tooling
  response=$(curl -s "$OLLAMA_API_BASE/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "'"$model"'",
      "messages": [{"role": "user", "content": "What is the weather in Paris?"}],
      "tools": '"$TOOLS_JSON"',
      "tool_choice": "auto"
    }')

  # Check if tool_calls are present
  if echo "$response" | jq -e '.choices[0].message.tool_calls' > /dev/null 2>&1; then
    echo "tooling-support : true : $model"
  else
    echo "tooling-support : false : $model"
  fi
done
