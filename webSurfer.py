import asyncio
import os

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_ext.models.openai import OpenAIChatCompletionClient

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"

async def main():
    # Initialize the OpenAI model client (GPT-4o recommended for multimodal capabilities)
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # Make sure to set your OPENAI_API_KEY environment variable
    )

    web_surfer_agent = MultimodalWebSurfer(
        name = "WebSurfer",
        model_client = model_client,
        headless= False,
        animate_actions=True
    )

    agent_team = RoundRobinGroupChat(participants=[web_surfer_agent],max_turns=3)

    await Console(agent_team.run_stream(task = "Navigate to Google and search for 'AutoGen framework Python'. Then summarize what "
                                 "you find."))

    await web_surfer_agent.close()
    await model_client.close()


asyncio.run(main())






