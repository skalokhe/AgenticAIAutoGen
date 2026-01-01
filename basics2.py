import asyncio
import os
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.ui import Console
from autogen_core import Image
from autogen_ext.models.openai import OpenAIChatCompletionClient

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"
async def main():
    multimodal_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    assistant = AssistantAgent(name="MultimodalAgentSK0", model_client=multimodal_client)
    image_path = Path("C:/Users/Sonal/OneDrive/Pictures/MEDHANSHWORK.png")
    image=Image.from_file(image_path)

    multiModalMessage = MultiModalMessage(
        content=["Describe the image", image], source="user"
    )
    await Console(assistant.run_stream(task=multiModalMessage))
    await multimodal_client.close()

asyncio.run(main())


