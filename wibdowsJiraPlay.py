import asyncio
import os
import sys
import shutil

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

# --- Environment variables (use your own secrets; avoid hardcoding in production) ---
os.environ[
    "OPENAI_API_KEY"] = "sk-proj-YOURAPIKEy"
os.environ["JIRA_URL"] = "https://sonalkalokhe89.atlassian.net"
os.environ["JIRA_USERNAME"] = "sonakalokhe.89@gmail.com"
os.environ[
    "JIRA_API_TOKEN"] = "JiraYOURAPIToken"
os.environ["JIRA_PROJECTS_FILTER"] = "CRED"

# --- Resolve executables on Windows ---
def resolve_executable(cmd_candidates):
    """
    Try multiple candidates (e.g., 'npx', 'npx.cmd') and return the first found on PATH.
    """
    for c in cmd_candidates:
        path = shutil.which(c)
        if path:
            return path
    return None

# Prefer exact executables on Windows
DOCKER_CMD = resolve_executable(["docker", "docker.exe"])
NPX_CMD = resolve_executable(["npx", "npx.cmd"])

if DOCKER_CMD is None:
    raise FileNotFoundError("Docker executable not found on PATH. Install Docker Desktop and ensure 'docker' is in PATH.")
if NPX_CMD is None:
    raise FileNotFoundError("npx not found on PATH. Install Node.js (which includes npm) and ensure 'npx' is in PATH.")

# --- Windows event loop policy (prevents actor shutdown warnings) ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    # Jira MCP server via Docker
    jira_server_params = StdioServerParams(
        command=DOCKER_CMD,
        args=[
            "run", "-i", "--rm",
            "--dns", "8.8.8.8", "--dns", "1.1.1.1",
            "-e", f"JIRA_URL={os.environ['JIRA_URL']}",
            "-e", f"JIRA_USERNAME={os.environ['JIRA_USERNAME']}",
            "-e", f"JIRA_API_TOKEN={os.environ['JIRA_API_TOKEN']}",
            "-e", f"JIRA_PROJECTS_FILTER={os.environ['JIRA_PROJECTS_FILTER']}",
            "ghcr.io/sooperset/mcp-atlassian:latest",
        ],
    )
    jira_workbench = McpWorkbench(jira_server_params)

    # Playwright MCP via npx
    playwright_server_params = StdioServerParams(
        command=NPX_CMD,
        args=[
            "@playwright/mcp@latest",
        ],
    )
    playwright_workbench = McpWorkbench(playwright_server_params)

    # Use context managers, then explicitly initialize
    async with jira_workbench as jira_wb, playwright_workbench as playwright_wb:
        # Ensure MCP actors are started
        #await jira_wb.initialize()
        #await playwright_wb.initialize()

        bug_analyst = AssistantAgent(
            name="BugAnalyst",
            model_client=model_client,
            workbench=jira_wb,
            system_message=(
                """
You are a Bug Analyst specializing in Jira defect analysis.

Your task is as follows:
Goal - - Your role is to analyze defects and create comprehensive test scenarios.
1. Retrieve and review the most recent **5 bugs** from the **CreditCardBanking Project** (Project Key: `CRED`) in Jira.
2. Carefully read their descriptions and identify **recurring issues or common patterns**.
3. Based on these patterns, design a **detailed user flow** that exercises the core features of the application and can serve as a robust **smoke test scenario**.

Be very specific in your smoke test design:
- Provide clear, step-by-step manual testing instructions.
- Include exact **URLs or page routes** to visit.
- Describe **user actions** (clicks, form inputs, submissions).
- Clearly state the **expected outcomes or validations** for each step.

If you detect **zero bugs** in the recent Jira query, attempt to re-query or note it clearly.

When your analysis and scenario preparation is complete:
- Clearly output the final smoke testing steps.
- Finally, write: **'HANDOFF TO AUTOMATION'** to signal completion of your analysis.
"""
            ),
        )

        automation_analyst = AssistantAgent(
            name="AutomationAgent",
            model_client=model_client,
            workbench=playwright_wb,
            system_message=(
                "You are a Playwright automation expert. Take the user flow from BugAnalyst "
                "and convert it into executable Playwright commands. Use Playwright MCP tools to "
                "execute the smoke test. Execute the automated test step by step and report "
                "results clearly, including any errors or successes. Take screenshots at key "
                "points to document the test execution."
                "Make sure expected results in the bug are validated in your flow"
                "Important : Use browser_wait_for to wait for success/error messages\n"
                "   - Wait for buttons to change state (e.g., 'Applying...' to complete)\n"
                "   - Verify expected outcomes as specified by BugAnalyst"
                " Always follow the exact timing and waiting instructions provided"
                "Complete ALL steps before saying 'TESTING COMPLETE, Execute each step fully, don't rush to completion"
            ),
        )

        # Initialize agents explicitly
        await bug_analyst.initialize()
        await automation_analyst.initialize()

        team = RoundRobinGroupChat(
            participants=[bug_analyst, automation_analyst],
            termination_condition=TextMentionTermination("TESTING COMPLETE"),
        )

        try:
            await Console(
                team.run_stream(
                    task=(
                        "BugAnalyst:\n"
                        "1. Search for recent bugs in CRED project\n"
                        "2. Then design a stable user flow that can be used as a smoke test.\n"
                        "3. Use REAL URLs like: https://rahulshettyacademy.com/seleniumPractise/#/\n\n"
                        "AutomationAgent:\n"
                        "Once ready, automate this flow using Playwright MCP and execute it."
                    )
                )
            )
        finally:
            # Clean shutdown
            await bug_analyst.close()
            await automation_analyst.close()

    # Close model client outside the workbench context
    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())