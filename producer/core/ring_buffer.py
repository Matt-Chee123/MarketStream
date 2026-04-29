

class RingBuffer:
    def __init__(self, capacity):
        if capacity <= 0 or (capacity & (capacity - 1)) != 0:
            raise ValueError(f"Capacity must be a values of 2, got {capacity}")

        self._capacity = capacity
        self._mask = capacity - 1
        self._buffer = [None] * capacity

        self._write_idx = 0
        self._read_idx = 0

    def pop(self):
        if self.is_empty():
            return None

        item = self._buffer[self._read_idx & self._mask]
        self._read_idx += 1
        return item

    def push(self, item):
        if self.is_full():
            return False

        self._buffer[self._write_idx & self._mask] = item
        self._write_idx += 1
        return True

    def is_empty(self):
        return self._write_idx == self._read_idx

    def size(self):
        return self._write_idx - self._read_idx

    def is_full(self):
        return self._write_idx - self._read_idx >= self._capacity