import json
import os

class Leaderboard:
    def __init__(self, filepath="leaderboard.json"):
        self.filepath = filepath
        self.scores = self.load()

    def load(self):
        """Load scores from the JSON file. Returns an empty list if file doesn't exist."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading leaderboard: {e}")
                return []
        return []

    def save(self):
        """Save the current scores to the JSON file."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.scores, f, indent=4)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def add_score(self, name, time):
        """Add a new score, sort the leaderboard by time (lowest first)."""
        self.scores.append({"name": name, "time": time})
        # Sort by time ascending
        self.scores = sorted(self.scores, key=lambda x: x["time"])
        self.save()

    def get_top_3(self):
        """Return the top 3 scores."""
        return self.scores[:3]
