import csv

class LatencyMonitor:
    def __init__(self, file_name):
        self.file_name = file_name
        self._file = open(file_name, "w", newline="", buffering=1)
        self._writer = csv.writer(self._file)

        self._writer.writerow([
            "t_binance_ms",
            "t_received_ns",
            "t_sent_ns",
        ])

    def write_row(self, t_binance_ms, t_received_ns, t_sent_ns):
        self._writer.writerow([t_binance_ms, t_received_ns, t_sent_ns])

    def close(self):
        self._file.close()