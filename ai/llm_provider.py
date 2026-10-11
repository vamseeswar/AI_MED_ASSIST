import os
from typing import Optional, List, Dict, Any, Generator
from backend.app.core.config import settings
from backend.app.core.logging import app_logger

# Cached LLM client
_GLOBAL_LLM_CLIENT = None


class BaseLLMClient:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    def stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    """Deterministic, fast mock LLM for testing and offline environments."""
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        prompt_lower = user_prompt.lower()
        if "hypertension" in prompt_lower:
            return (
                "Hypertension (high blood pressure) is defined clinically as systolic blood pressure ≥ 130 mm Hg "
                "or diastolic blood pressure ≥ 80 mm Hg according to modern cardiology guidelines. "
                "Primary lifestyle interventions include adherence to the DASH diet, reduction in dietary sodium, "
                "and regular aerobic exercise."
            )
        elif "dyspnea" in prompt_lower:
            return (
                "Dyspnea is defined clinically as the sensation of breathing difficulty or shortness of breath. "
                "It serves as a primary symptom across various cardiovascular, pulmonary, and metabolic pathologies."
            )
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return (
                "Document Executive Summary:\n"
                "The analyzed document outlines clinical methodology, patient cohort observations, "
                "and therapeutic outcomes. Key laboratory markers demonstrated measurable improvements "
                "under structured protocol monitoring."
            )
        elif "compare" in prompt_lower:
            return (
                "Document Comparison Analysis:\n"
                "- Similarities: Both documents analyze cardiovascular patient outcomes.\n"
                "- Differences: Document A emphasizes pharmacological interventions whereas Document B focuses on lifestyle modifications."
            )
        else:
            return (
                f"Medical Information Analysis:\n"
                f"Based on the provided medical documentation, the evidence indicates established physiological "
                f"mechanisms and clinical guideline standards related to your inquiry."
            )

    def stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        full_text = self.generate(system_prompt, user_prompt)
        words = full_text.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i + 3]) + " "
            yield chunk


class GeminiLLMClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", temperature: float = 0.2):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self._init_client()

    def _init_client(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": self.temperature}
            )
            app_logger.info(f"Initialized Google Gemini LLM ({self.model_name}) successfully.")
        except Exception as exc:
            app_logger.warning(f"Failed to initialize Google Gemini client: {exc}. Using mock fallback.")
            self.model = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.model:
            return MockLLMClient().generate(system_prompt, user_prompt)

        try:
            full_prompt = f"System Instructions:\n{system_prompt}\n\nUser Request:\n{user_prompt}"
            response = self.model.generate_content(full_prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as exc:
            app_logger.error(f"Gemini generation call failed: {exc}, using mock fallback.")
            return MockLLMClient().generate(system_prompt, user_prompt)

    def stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        if not self.model:
            for piece in MockLLMClient().stream(system_prompt, user_prompt):
                yield piece
            return

        try:
            full_prompt = f"System Instructions:\n{system_prompt}\n\nUser Request:\n{user_prompt}"
            response = self.model.generate_content(full_prompt, stream=True)
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
        except Exception as exc:
            app_logger.error(f"Gemini streaming failed: {exc}, falling back to mock stream.")
            for piece in MockLLMClient().stream(system_prompt, user_prompt):
                yield piece


class OpenAILLMClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.2):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        try:
            from langchain_openai import ChatOpenAI
            self.chat = ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.api_key,
                temperature=self.temperature
            )
        except Exception:
            self.chat = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.chat:
            return MockLLMClient().generate(system_prompt, user_prompt)
        from langchain_core.messages import SystemMessage, HumanMessage
        response = self.chat.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        return response.content

    def stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        if not self.chat:
            for piece in MockLLMClient().stream(system_prompt, user_prompt):
                yield piece
            return
        from langchain_core.messages import SystemMessage, HumanMessage
        for chunk in self.chat.stream([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]):
            yield chunk.content


class GroqLLMClient(BaseLLMClient):
    """Production Groq LLM client for high-throughput, low-latency medical intelligence."""
    def __init__(self, api_key: str, model_name: str = "openai/gpt-oss-120b", temperature: float = 0.2):
        self.api_key = api_key
        self.model_name = model_name or "openai/gpt-oss-120b"
        self.temperature = temperature
        self._init_client()

    def _init_client(self):
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            app_logger.info(f"Initialized Groq LLM ({self.model_name}) successfully.")
        except Exception as exc:
            app_logger.warning(f"Failed to initialize Groq client: {exc}. Using mock fallback.")
            self.client = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            return MockLLMClient().generate(system_prompt, user_prompt)

        candidate_models = [self.model_name]
        for fallback in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_error = None
        for model in candidate_models:
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=model,
                    temperature=self.temperature
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                last_error = exc
                app_logger.warning(f"Groq generation call failed on model '{model}': {exc}. Trying fallback...")
                continue

        app_logger.error(f"All Groq models failed: {last_error}, using mock fallback.")
        return MockLLMClient().generate(system_prompt, user_prompt)

    def stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        if not self.client:
            for piece in MockLLMClient().stream(system_prompt, user_prompt):
                yield piece
            return

        candidate_models = [self.model_name]
        for fallback in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_error = None
        for model in candidate_models:
            try:
                stream_resp = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=model,
                    temperature=self.temperature,
                    stream=True
                )
                for chunk in stream_resp:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as exc:
                last_error = exc
                app_logger.warning(f"Groq streaming call failed on model '{model}': {exc}. Trying fallback...")
                continue

        app_logger.error(f"All Groq streaming models failed: {last_error}, falling back to mock stream.")
        for piece in MockLLMClient().stream(system_prompt, user_prompt):
            yield piece


def reset_llm_client():
    """Reset cached global LLM client to force re-instantiation."""
    global _GLOBAL_LLM_CLIENT
    _GLOBAL_LLM_CLIENT = None


def get_llm_client() -> BaseLLMClient:
    """Factory returning the active LLM client based on environment config."""
    global _GLOBAL_LLM_CLIENT
    if _GLOBAL_LLM_CLIENT is not None:
        return _GLOBAL_LLM_CLIENT

    provider = settings.LLM_PROVIDER.lower()
    groq_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")

    if provider == "mock":
        _GLOBAL_LLM_CLIENT = MockLLMClient()
    elif provider == "groq" and groq_key:
        _GLOBAL_LLM_CLIENT = GroqLLMClient(
            api_key=groq_key,
            model_name=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
    elif provider == "gemini" and settings.GOOGLE_API_KEY:
        _GLOBAL_LLM_CLIENT = GeminiLLMClient(
            api_key=settings.GOOGLE_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
    elif provider == "openai" and settings.OPENAI_API_KEY:
        _GLOBAL_LLM_CLIENT = OpenAILLMClient(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
    elif groq_key:
        # Auto-detect Groq if key is present
        _GLOBAL_LLM_CLIENT = GroqLLMClient(
            api_key=groq_key,
            model_name=settings.LLM_MODEL or "openai/gpt-oss-120b",
            temperature=settings.LLM_TEMPERATURE
        )
    else:
        # Fallback to mock provider
        _GLOBAL_LLM_CLIENT = MockLLMClient()

    return _GLOBAL_LLM_CLIENT


get_llm_provider = get_llm_client

