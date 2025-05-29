import asyncio
import json
from pathlib import Path
from autogen_agentchat.base import Response
from typing import List, Union
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import BaseChatMessage, ChatMessage

class CodeWriterAgent(BaseChatAgent):
    def __init__(
        self,
        name: str,
        work_dir: Union[str, Path] = "out",
        description: str = "A code writer that writes code blocks to files without executing them.",
    ):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(name=name, description=description)


    async def on_messages(self, messages: List[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        last_msg = messages[-1].content
        if not last_msg or not last_msg.strip():
            return Response(chat_message=TextMessage(content="Error: Received empty message content.", source=self.name))

        code_blocks_data = json.loads(last_msg)
        if isinstance(code_blocks_data, dict):
            files = self.write_code_blocks(code_blocks_data)
            file_list = "\n".join(str(f) for f in files)
            return Response(chat_message=TextMessage(
                content=f"Wrote the following files:\n{file_list}",
                source=self.name,
            ))
        else:
            return Response(chat_message=TextMessage(
                content=f"Invalid code format",
                source=self.name,
            ))


    def on_reset(self, cancellation_token: CancellationToken) -> List[type[BaseChatMessage]]:
        pass

    @property
    def produced_message_types(self) -> List[type[BaseChatMessage]]:
        return [ChatMessage]

    def write_code_blocks(self, code_block: dict) -> List[Path]:
        written_files = []
        code = code_block["code"]
        filename = code_block["filename"]
        file_path = self.work_dir / filename
        file_path.write_text(code, encoding="utf-8")
        written_files.append(file_path)
        return written_files


async def main():
    code_writer = CodeWriterAgent(name="code_writer", work_dir="out")
    payload = {
        "filename": "example.ts",
        "code": "console.log('TS code block');"
    }
    message = TextMessage(content=json.dumps(payload, indent=2), source="mock_code_writer")
    response = await code_writer.on_messages(messages=[message],  cancellation_token=CancellationToken())
    print(response.chat_message.content)

if __name__ == "__main__":
    asyncio.run(main())
