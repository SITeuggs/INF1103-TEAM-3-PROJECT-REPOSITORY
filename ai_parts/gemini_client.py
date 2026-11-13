import logging
from ai_parts.ai_client import AIClient
from errors.ai_error import AIError

class GeminiClient(AIClient):
    def __init__(self, api_key, model, timeout_seconds):
        self._model = model
        self.__client = None
        self.__problem = ""
        logging.getLogger("google_genai").setLevel(logging.ERROR)
        try:
            from google import genai
            from google.genai import types
            try:
                options = types.HttpOptions(timeout=timeout_seconds * 1000)
                self.__client = genai.Client(api_key=api_key,
                                             http_options=options)
            except (TypeError, AttributeError):
                self.__client = genai.Client(api_key=api_key)
        except Exception as error:
            self.__problem = str(error)

    def generate(self, system_prompt, contents, max_tokens):
        if self.__client is None:
            raise AIError("Gemini is not set up: " + self.__problem)
        settings = {
            "system_instruction": system_prompt,
            "max_output_tokens": max_tokens,
        }
        try:
            response = self.__client.models.generate_content(
                model=self._model, config=settings, contents=contents)
            return response.text
        except Exception as error:
            raise AIError(str(error))
