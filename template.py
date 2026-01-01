import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"
async def main():

    openai_model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")


asyncio.run(main())


