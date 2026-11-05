
class BasicMemory:
    def __init__(self, max_messages=10):
        self.max_messages = max_messages
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
        self.messages = self.messages[-self.max_messages:]

    def get_messages(self):
        return self.messages.copy()

    def clear(self):
        self.messages = []
