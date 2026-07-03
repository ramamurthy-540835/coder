import logging
from .shared import call_grok_43_reasoning

logger = logging.getLogger(__name__)

class Agent3_DevSecOpsAudit:
    def audit(self, design_spec, stack):
        logger.info("[AGENT 3] Security & Compliance Audit...")
        prompt = f"""Audit this design for {stack['primary_language']} security issues and give fix directives:

{design_spec}"""
        return call_grok_43_reasoning(prompt)
