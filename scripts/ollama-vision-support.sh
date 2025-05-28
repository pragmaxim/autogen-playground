#!/bin/bash

# This script checks which locally installed Ollama models support vision input.

# Check if an image path is provided
if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/sample_image.jpg"
  exit 1
fi

if [ -z "$OLLAMA_API_BASE" ]; then
  echo "export OLLAMA_API_BASE=http://localhost:11434"
  exit 1
fi

IMAGE_PATH="$1"

# Verify that the image file exists
if [ ! -f "$IMAGE_PATH" ]; then
  echo "Error: File '$IMAGE_PATH' not found."
  exit 1
fi

# Encode the image in base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH")

# Get list of local models
models=$(ollama ls | awk 'NR>1 {print $1}')

for model in $models; do
  # Create a temporary JSON payload
  payload_file=$(mktemp)
  cat > "$payload_file" <<EOF
{
  "model": "$model",
  "messages": [
    {
      "role": "user",
      "content": "What is in this image?",
      "images": ["data:image/jpeg;base64,${IMAGE_BASE64}"]
    }
  ]
}
EOF

  # Send the request using the payload file
  response=$(curl -s "$OLLAMA_API_BASE/v1/chat/completions" \
    -H "Content-Type: application/json" \
    --data @"$payload_file")

  rm -f "$payload_file"  # Clean up temp file

  # Check if the response contains a valid answer
  if echo "$response" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
    echo "vision-support : true : $model"
  else
    echo "vision-support : false : $model"
  fi
done
