import asyncio
import os

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"

async def main():

    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    ## Agent 1
    agentAI = AssistantAgent(name="MathTutor",model_client=model_client,
                   system_message="you are a helpful math tutor, help the user solve math problems step by step"
                                  "When user says 'THANKS DONE' or similar , acknowledge and say 'LESSON COMPLETE' to end session")


    ## Human Interaction in augen we have classs userproxyagent,
    # other party is human they have brain so no need of model client

    user = UserProxyAgent(name="student")
    team = RoundRobinGroupChat( participants=[user, agentAI],
                         termination_condition=TextMentionTermination("LESSON COMPLETE") )

    await Console(team.run_stream(task = "Need help with Algebra problem, can you help me solve 4+5*3/2+(1+1)"))
    await model_client.close()
asyncio.run(main())


