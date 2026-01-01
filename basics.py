import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"
async def main():
    print("my basic program")
    openai_model_client = OpenAIChatCompletionClient(  # LLM this is LLM used by me
        model="gpt-4o-mini"
        # api_key="sk-...", # Optional if you have an OPENAI_API_KEY environment variable set.
    )
    #//create agent and it has to respond back
    assistant=AssistantAgent(name="AssistantAgentSK",model_client=openai_model_client)
    await Console(assistant.run_stream(task="describe masai mara")) #rela time streaming of output, else same as run
    await openai_model_client.close()

asyncio.run(main())


