import os
import json

class StateManager:
    def __init__(self, seen_filepath):
        self.seen_filepath = seen_filepath
        self.seen_links = set()
        self.load()

    def load(self):
        if os.path.exists(self.seen_filepath):
            try:
                with open(self.seen_filepath, 'r', encoding='utf-8') as f:
                    self.seen_links = set(json.load(f))
            except Exception as e:
                print(f"Error loading state from {self.seen_filepath}: {e}")

    def save(self):
        try:
            with open(self.seen_filepath, 'w', encoding='utf-8') as f:
                json.dump(list(self.seen_links), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving state to {self.seen_filepath}: {e}")

    def is_new(self, link):
        return link not in self.seen_links

    def add(self, link):
        self.seen_links.add(link)
