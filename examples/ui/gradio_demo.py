import os
import sys
sys.path.insert(0, os.path.abspath("."))  # 현재 디렉토리를 가장 먼저 검색하도록
import asyncio
from dataclasses import dataclass
from typing import List, Optional

# Third-party imports
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Local module imports
from browser_use import Agent

load_dotenv()


@dataclass
class ActionResult:
	is_done: bool
	extracted_content: Optional[str]
	error: Optional[str]
	include_in_memory: bool


@dataclass
class AgentHistoryList:
	all_results: List[ActionResult]
	all_model_outputs: List[dict]


def parse_agent_history(history_str: str) -> None:
	console = Console()

	# Split the content into sections based on ActionResult entries
	sections = history_str.split('ActionResult(')

	for i, section in enumerate(sections[1:], 1):  # Skip first empty section
		# Extract relevant information
		content = ''
		if 'extracted_content=' in section:
			content = section.split('extracted_content=')[1].split(',')[0].strip("'")

		if content:
			header = Text(f'Step {i}', style='bold blue')
			panel = Panel(content, title=header, border_style='blue')
			console.print(panel)
			console.print()


async def run_browser_task(
	task: str,
	api_key: str,
	model: str = 'gpt-4o',
	headless: bool = True,
) -> str:
	if not api_key.strip():
		return 'Please provide an API key'

	os.environ['OPENAI_API_KEY'] = api_key

	# 민감한 데이터 정의
	sensitive_data = {
		'github_username': 'wkdwo8703@gmail.com',
		'github_password': '@'
	}

	try:
    
# 		task = """
# Go to dev.msaez.io

# When github login page appears:
# 1. Input <secret>github_username</secret> into username field
# 2. Input <secret>github_password</secret> into password field
# 3. Click sign in button
# 4. If "Authorize msa-ez" button appears, click it

# After login:
# 1. Click the "만들기" button and select "생성" of "이벤트스토밍"

# 2. Go to https://dev.msaez.io/#/storming/b4466f9f6576d82217e90b9bb4b58a5d

# 3. For finding the BoundedContext:
#    - Click each sticker in the left toolbar one by one
#    - When you click a sticker, check if it shows "Bounded Context" in its tooltip
#    - Once you find the sticker that shows "Bounded Context", that's our target
#    - Remember that element's index

# 4. Once the correct BoundedContext sticker is found, drag it to coordinates (500, 300)
# """
		agent = Agent(
			task=task,
			llm=ChatOpenAI(model='gpt-4o'),
			sensitive_data=sensitive_data  # 민감 데이터 전달
		)
		result = await agent.run()
		#  TODO: The result cloud be parsed better
		return str(result)  # Convert AgentHistoryList to string
	except Exception as e:
		return f'Error: {str(e)}'


def create_ui():
	with gr.Blocks(title='Browser Use GUI') as interface:
		gr.Markdown('# Browser Use Task Automation')

		with gr.Row():
			with gr.Column():
				api_key = gr.Textbox(label='OpenAI API Key', placeholder='sk-...', type='password')
				task = gr.Textbox(
					label='Task Description',
					placeholder='E.g., Find flights from New York to London for next week',
					lines=3,
				)
				model = gr.Dropdown(
					choices=['gpt-4', 'gpt-3.5-turbo'], label='Model', value='gpt-4'
				)
				headless = gr.Checkbox(label='Run Headless', value=True)
				submit_btn = gr.Button('Run Task')

			with gr.Column():
				output = gr.Textbox(label='Output', lines=10, interactive=False)

		submit_btn.click(
			fn=lambda *args: asyncio.run(run_browser_task(*args)),
			inputs=[task, api_key, model, headless],
			outputs=output,
		)

	return interface


if __name__ == '__main__':
	demo = create_ui()
	demo.launch()