# config.py (create this)
MODELS = {
    "grok": {
        "provider": "xai",
        "model_name": "grok-3",           # or whatever current Grok model
        "api_key_env": "XAI_API_KEY"
    },
    "claude": {
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "codex": {                            # OpenAI-style / GPT-4o
        "provider": "openai",
        "model_name": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY"
    },
    "gemini": {
        "provider": "google",
        "model_name": "gemini-3.0-flash",
        "api_key_env": "GOOGLE_API_KEY"
    },
    "local": {
        "provider": "local",
        "model_name": "your-local-model",
        "base_url": "http://localhost:11434/v1"
    }
}

DEFAULT_MODEL = "grok"
