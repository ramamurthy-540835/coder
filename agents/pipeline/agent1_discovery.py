import json
import logging
from .shared import call_grok_43_reasoning

logger = logging.getLogger(__name__)

class Agent1_StackDiscovery:
    def analyze(self, spec):
        logger.info("[AGENT 1] Tech Stack Discovery...")
        prompt = f"""Analyze this project spec and choose the BEST tech stack (no Python bias):

{spec}

Return JSON only:
{{"primary_language": "...", "framework": "...", "rationale": "...", "required_folders": [], "dependencies": {{}}, "core_requirements": []}}"""
        return json.loads(call_grok_43_reasoning(prompt, json_mode=True))
