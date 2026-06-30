from openai import OpenAI

from app.core.config import settings

class LLMClient:
    def __init__(self) -> None:
        if not settings.llm_base_url:
            raise ValueError("LLM_BASE_URL 不能为空")
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY 不能为空")
        if not settings.llm_model:
            raise ValueError("LLM_MODEL 不能为空")
        self.client  = OpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            timeout=settings.llm_timeout,
        )
        self.model_name = settings.llm_model

    def chat(self,
            system_prompt:str,
            user_prompt:str,) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role":"system",
                        "content":system_prompt,
                    },
                    {
                        "role":"user",
                        "content":user_prompt,
                    },
                ],
                temperature=0.2
            )
            content = response.choices[0].message.content
            if not content:
                return ""
            return content
        except Exception as e:
            raise RuntimeError(e) from e
llm_client = LLMClient()