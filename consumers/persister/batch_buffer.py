import time

class BatchBuffer:
    def __init__(self, max_rows, max_seconds):
        self.max_rows = max_rows
        self.max_seconds = max_seconds
        self.rows = []
        self.first_added_at = None

    def add(self, row):
        if not self.first_added_at:
            self.first_added_at = time.monotonic()
        self.rows.append(row)

    def should_flush(self):
        if not self.rows:
            return False
        if len(self.rows) >= self.max_rows:
            return True
        if time.monotonic() - self.first_added_at >= self.max_seconds:
            return True
        return False

    def drain(self):
        rows = self.rows
        self.rows = []
        self.first_added_at = None
        return rows