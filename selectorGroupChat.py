# How to dynamically  choose which agent to act in teams ,
# its costly so in case you are sure about the sequence use RoundRobin
import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"
async def main():

    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    agent1_Researcher = AssistantAgent( name="agent_1Researcher",
                                        model_client=model_client,
                                        system_message="You are a researcher. Your role os to gather information and provide research findings"
                                                       "Do not write articles or create content - just provide research data and facts."

                                       )

    agent2_Writer = AssistantAgent(name="agent2_Writer",
                                   model_client=model_client,
                                   system_message="You are a writer. Your role is to take research information and "
                                                  "create well writtem articles. Wait for the research to be provided, then write the content in a readable draft"
                                   )

    agent3_Critics = AssistantAgent(name="agent3_Critics",
                                    model_client=model_client,
                                    system_message="You are a critics. Your role is to Review written content and provide feedback"
                                                   "Say 'TERMINATE' when satisfied with the final result. "
                                    )

    text_termination = TextMentionTermination("TERMINATE")

    max_messageTermination = MaxMessageTermination( max_messages=10 )

    terminationCondition = text_termination | max_messageTermination

    team = SelectorGroupChat( participants=[agent3_Critics, agent2_Writer, agent1_Researcher],
                              termination_condition=terminationCondition,
                              allow_repeated_speaker=True,
                              model_client=model_client)

    await Console(team.run_stream(task=" Todays Political scenes across world and future of the diplomacy and what will be the future wars or competitions among contires across globe look like"))

    await model_client.close()
asyncio.run(main())

