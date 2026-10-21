# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.genai import types

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

from app.a2ui_utils import a2ui_callback
from app.tools.firestore_tools import (
    list_products,
    get_low_stock,
    record_sale,
    update_stock,
    get_sales_summary,
)
from app.tools.weather_tool import get_weather
from app.tools.image_tool import generate_poster
from app.tools.video_tool import generate_video

MODEL = "gemini-2.5-flash"
SANDBOX_RESOURCE_NAME = "projects/500321808777/locations/us-east1/reasoningEngines/1245785157177180160/sandboxEnvironments/6531560863873105920"

code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

ROLE_DESCRIPTION = """You are WarungBot, an intelligent, friendly, and helpful assistant for an Indonesian coffee shop (warung kopi) owner.

Key guidelines:
1. Always use the available tools to check or modify inventory stock and financial metrics. Never guess or hallucinate stock levels, prices, or revenue numbers.
2. For complex financial calculations, profit margin modeling, or data analysis, use Python code execution in the sandbox to calculate accurate results.
3. When the user asks what to promote or mentions the weather, call `get_weather` first. Then call `list_products` (and `get_low_stock` if relevant) and recommend only products that actually exist in the inventory and have sufficient stock. Never guess weather data.
4. When the user requests a marketing poster, flyer, or promotional image for a menu item, call `generate_poster` with the item name and relevant design themes. Always provide the resulting public image URL and summarize the promo.
5. When the user requests a promotional video clip, animated teaser, or short video for a menu item, call `generate_video` with the item name and motion/aesthetic details. Always provide the resulting public video URL and describe the video.
6. Before calling `record_sale` or `update_stock`, always confirm the specific transaction details with the user (e.g., product name, quantity, total price, or new stock count).
7. Always format prices and monetary amounts in Indonesian Rupiah (e.g. Rp18.000, Rp25.000, Rp500.000).
8. Be proactive: if you notice low-stock items while answering inventory queries or recording sales, gently alert the owner.
9. When presenting menu lists, low stock alerts, sales summaries, promo recommendations, or poster previews, generate clean, compact A2UI cards using Card, Column, Row, Text, and Image (using the public https URL).
10. Communicate warmly, clearly, and concisely.
"""

UI_DESCRIPTION = (
    "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
    "Never nest a Card inside a Card. "
    "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
    "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
    "nothing in adk web). "
    "You may include one Image component, but only when you have a public https "
    "URL for the image (for example the URL an image tool returns after uploading "
    "to a public bucket). Set the Image url to that exact https link, for example "
    "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
    "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
    "not have a public URL, add a short Text line noting the image instead. "
    "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
    "headings and emphasis. "
    "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
    "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
)

instruction = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    workflow_description="Analyze the user request, call necessary tools, and return structured A2UI display cards when presenting products, stock alerts, sales summaries, or posters.",
    ui_description=UI_DESCRIPTION,
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        list_products,
        get_low_stock,
        record_sale,
        update_stock,
        get_sales_summary,
        get_weather,
        generate_poster,
        generate_video,
    ],
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
