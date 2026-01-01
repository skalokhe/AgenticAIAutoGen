import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"
os.environ["JIRA_USERNAME"] = "sonakalokhe.89@gmail.com"
os.environ[
    "JIRA_API_TOKEN"] = "JUORJIRAAPIKEY"
os.environ["JIRA_PROJECTS_FILTER"] = "CRED"


async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    mcpConfigParam_jira = StdioServerParams(
        command="docker",
        args=[
            "run",
            "-i",
            "--rm",
            "-e", f"JIRA_URL = {os.environ['JIRA_URL']}",
            "-e", f"JIRA_USERNAME = {os.environ['JIRA_USERNAME']}",
            "-e", f"JIRA_API_TOKEN = {os.environ['JIRA_API_TOKEN']}",
            "-e", f"JIRA_PROJECTS_FILTER  = {os.environ['JIRA_PROJECTS_FILTER']}",
            "ghcr.io/sooperset/mcp-atlassian:latest"
        ],

    )

    mcpConfigParam_playwright = StdioServerParams(
        command="npx",
        args=["@playwright/mcp@latest"]


    )

    jira_workbench = McpWorkbench(mcpConfigParam_jira)
    playwright_workbench = McpWorkbench(mcpConfigParam_playwright)

    async with jira_workbench as jira_wb:
        bug_analyst = AssistantAgent(name="BugAnalyst", model_client=model_client,
                                     workbench=jira_wb, system_message=(
                "You are a Playwright automation expert. Take the user flow from BugAnalyst "
                "and convert it into executable Playwright commands. Use Playwright MCP tools to  "
                "execute the smoke test. Execute the automated test step by step and report "
                "results clearly, including any errors or successes. Take screenshots at key "
                "points to document the test execution."
                "Make sure expected results in the bug are validated in your flow"
                "Important : Use browser_wait_for to wait for success/error messages\n"
                "   - Wait for buttons to change state (e.g., 'Applying...' to complete)\n"
                "   - Verify expected outcomes as specified by BugAnalyst"
                " Always follow the exact timing and waiting instructions provided"
                "Complete ALL steps before saying 'TESTING COMPLETE, Execute each step fully, don't rush to completion"))


    async with playwright_workbench as playwright_wb:
        automation_agent = AssistantAgent(name="AutomationAgent", model_client=model_client,
                                          workbench=playwright_wb, system_message=(
                "You are a Playwright automation expert. Take the user flow from BugAnalyst "
                "and convert it into executable Playwright commands. Use Playwright MCP tools to  "
                "execute the smoke test. Execute the automated test step by step and report "
                "results clearly, including any errors or successes. Take screenshots at key "
                "points to document the test execution."
                "Make sure expected results in the bug are validated in your flow"
                "Important : Use browser_wait_for to wait for success/error messages\n"
                "   - Wait for buttons to change state (e.g., 'Applying...' to complete)\n"
                "   - Verify expected outcomes as specified by BugAnalyst"
                " Always follow the exact timing and waiting instructions provided"
                "Complete ALL steps before saying 'TESTING COMPLETE, Execute each step fully, don't rush to completion"))


    team = RoundRobinGroupChat(participants=[bug_analyst, automation_agent],
                               termination_condition=TextMentionTermination('TESTING COMPLETE'))



    await Console(team.run_stream(task="bug_analyst \n"
                                       "1. Search for recent bugs in CRED project \n"
                                       "2. Then design a stable user flow that can be used as a smoke test.\n"
                                       "3. Use REAL URL's like https://rahulshetyacademy.com/seleniumPractise/#/"
                                       "automation_agent : \n"
                                       "Once Ready, automate this flow using Playwright MCP and execute it."))

    await model_client.close()


asyncio.run(main())
