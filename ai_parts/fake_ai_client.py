from ai_parts.ai_client import AIClient

class FakeAIClient(AIClient):
    def __init__(self, replies):
        self._replies = list(replies)
        self._calls = 0
        self._last_contents = ""

    @property
    def calls(self):
        return self._calls

    @property
    def last_contents(self):
        return self._last_contents

    def generate(self, system_prompt, contents, max_tokens):
        index = self._calls
        if index >= len(self._replies):
            index = len(self._replies) - 1
        self._calls = self._calls + 1
        self._last_contents = contents
        reply = self._replies[index]
        if isinstance(reply, Exception):
            raise reply
        return reply
