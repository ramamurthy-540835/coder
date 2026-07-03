import logging
from .shared import call_grok_43_reasoning

logger = logging.getLogger(__name__)

class Agent2_SystemDesign:
    def design(self, spec, stack):
        logger.info("[AGENT 2] System Architecture Design...")
        prompt = f"""Design full architecture for:
Language: {stack['primary_language']} / Framework: {stack.get('framework')}

Spec: {spec}

Include ASCII diagrams, data model, security boundaries, file layout."""
        return call_grok_43_reasoning(prompt)
