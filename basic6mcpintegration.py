import asyncio
import os

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"

async def main():
    # integrate mcp the class StdioServerParams https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
    # configuration
    filesystem_mcp_config = StdioServerParams( command = "npx",
                                               args= [
                                                       "-y",
                                                       "@modelcontextprotocol/server-filesystem",
                                                       "C:/Users/Sonal/PycharmProjects/PythonProject/PythonProject/agenticAIAutoGen"
                                                     ],
                                               read_timeout_seconds = 10
                                            )

    # start the mcp server by passing the above coniguration and pass the . will get instance of the mcp server
    fsmcp_workbench = McpWorkbench(filesystem_mcp_config)

    async with fsmcp_workbench as fs_wb :

        model_client = OpenAIChatCompletionClient( model="gpt-4o" )


        # 1 .workbench tooling support added to the agent
        # 2. get instance of mcp server
        # 3. which server to start is mentioned in the stdioServerParam
        # 4. asynch= in nature and  needs to be handled inside this block
        # 5 go to official mcp documentation where you get the configuration ,node should be installed in the system else it wont work

        assistant = AssistantAgent( name="MathTutor", model_client=model_client, workbench=fs_wb,
                                    system_message="You are helpful math tutor.Help the user solve math problems step by step"
                                                   "You have to access file system"
                                                   "When the user says 'THANKS DONE' or similar, acknowledge and say 'LESSON COMPLETE' to end session." )

        user_proxy = UserProxyAgent( name="Student" )

        ## RoundRobin sequence of agent matters  user is initiator so needs to pass first
        team = RoundRobinGroupChat( participants=[user_proxy, assistant],
                                    termination_condition=TextMentionTermination( "LESSON COMPLETE" ) )

        await Console(team.run_stream(task = "I need help with algebra problem. Tutor feel to create files to help student with learning"))
        await model_client.close()

asyncio.run( main() )


#Human - Agent-(save)  ,Agent2 (save)
