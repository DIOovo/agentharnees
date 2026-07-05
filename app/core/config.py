import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "")
    llm_timeout: int = int(os.getenv("LLM_TIMEOUT", "60"))
    runner_mode: str = os.getenv("RUNNER_MODE", "fake")
    sandbox_image:str = os.getenv("SANDBOX_IMAGE", "agent-harness-sandbox:latest")
    sandbox_timeout: int = int(os.getenv("SANDBOX_TIMEOUT", "20"))
    sandbox_memory: str = os.getenv("SANDBOX_MEMORY", "512m")
    sandbox_cpus: str = os.getenv("SANDBOX_CPUS", "1")
settings = Settings()