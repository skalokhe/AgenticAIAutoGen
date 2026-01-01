import asyncio
import json
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"
async def main():

    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    agent1 = AssistantAgent(name="SKAgent1", model_client=model_client)

    agent2 = AssistantAgent(name="SKAgent2", model_client=model_client)

    await Console( agent1.run_stream(task="My Fauorite sports person is Ronaldo ") )
    state = await agent1.save_state()

    #write to file
    with open("stateMemory.json", "w") as f:
        json.dump(state, f, default=str)

    #read from file
    with open("stateMemory.json", "r") as f:
        saved_state = json.load(f)

    #load the saved state from agent1 to agent 2
    await agent2.load_state(saved_state)

    await Console( agent2.run_stream(task=" What is my favorite sport person "))

    #close the model client
    await model_client.close()

asyncio.run(main())

## Start with Free LLM (for easy tasks ) and save state given to paid LLM  reason  they dont eant to start converation with paod as it consumes token and money starts burning
## carefully saving money / cost of tokens

## when agent1 goes down and chatbot opens again it should start from there

