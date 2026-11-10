from abc import ABC, abstractmethod

class AIClient(ABC):
    @abstractmethod
    def generate(self, system_prompt, contents, max_tokens):
        pass
