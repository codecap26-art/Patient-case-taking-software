import os
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
import instructor
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.core.config import settings

# Load .env from backend root
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_file = os.path.join(backend_root, ".env")
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMProvider:
    """
    Configurable LLM provider ported from DoctorAI repository.
    Supports OpenAI-compatible endpoints (Groq, Gemini, OpenAI) with
    Instructor patching for strictly validated clinical Pydantic outputs.
    """

    def __init__(self):
        self._init_client()

    def _init_client(self):
        groq_key = os.getenv("GROQ_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)

        # 1. Prefer Groq if available (ultra-fast inference, OpenAI-compatible)
        if groq_key and groq_key.startswith("gsk_"):
            self.api_key = groq_key
            self.base_url = "https://api.groq.com/openai/v1"
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            logger.info("DoctorAI LLM configured with Groq (%s)", self.model)
        # 2. Check Gemini OpenAI-compatible endpoint
        elif gemini_key:
            self.api_key = gemini_key
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            self.model = "gemini-1.5-flash"
            logger.info("DoctorAI LLM configured with Gemini OpenAI endpoint (%s)", self.model)
        # 3. Default OpenAI compatible / settings fallback
        else:
            self.api_key = os.getenv("AI_API_KEY", "dummy-key")
            self.base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
            self.model = os.getenv("AI_MODEL", "gpt-4o")
            logger.info("DoctorAI LLM configured with OpenAI endpoint (%s)", self.model)

        self.raw_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=30.0,
        )
        self.client = instructor.from_openai(self.raw_client)

    async def generate_structured(self, system_prompt: str, user_message: str, response_model: Type[T]) -> T:
        """
        Generate structured response adhering strictly to the given Pydantic model.
        """
        try:
            return await self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
                max_retries=2,
            )
        except Exception as e:
            logger.warning("DoctorAI LLM structured generation failed: %s", e)
            raise

    async def generate_text(self, system_prompt: str, user_message: str) -> str:
        """
        Generate plain text response with clinical reasoning using raw AsyncOpenAI client.
        """
        try:
            response = await self.raw_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.warning("DoctorAI LLM text generation failed: %s", e)
            raise


llm_provider = LLMProvider()
