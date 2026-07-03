import json
import logging
from .shared import call_grok_43_reasoning

logger = logging.getLogger(__name__)

class Agent4_PolyglotCompiler:
    def compile(self, spec, stack, design, audit, prompt_id):
        logger.info("[AGENT 4] Polyglot Code Generation...")
        prompt = f"""Generate COMPLETE production code for the following tech stack:

{json.dumps(stack)}

Design: {design}
Audit Directives: {audit}

Return JSON only:
{{"project_name": "...", "files": {{"path/to/file.ext": "full code here", ...}}}}"""
        return json.loads(call_grok_43_reasoning(prompt, json_mode=True))
