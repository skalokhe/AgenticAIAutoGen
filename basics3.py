import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"

async def main():

    #create first assistant agent math teacher
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    agent1 = AssistantAgent( name="MathTeacher", model_client=model_client,
                             system_message="You are a Mathematics Teacher,Explain concepts clearly with examples , day to day usecases  and ask follow-up"
                                            "questions" )
    # create  2nd assistant agent as student
    agent2 = AssistantAgent( name="Student", model_client=model_client,
                             system_message="You are a curious student. Ask Questions and show your thinking process")

    # class roundrobin group chat to collaborate between agents

    team = RoundRobinGroupChat( participants=[agent1,agent2],
                               termination_condition=MaxMessageTermination( max_messages=6 ) )

    await Console(team.run_stream( task="Let's discuss what is multiplication and how it works and used in daily life") )
    await model_client.close()

asyncio.run(main())
