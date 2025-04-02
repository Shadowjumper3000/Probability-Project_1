import numpy as np


class QueueTracker:
    """Tracks queue statistics for airport stations"""

    def __init__(self):
        self.queue_lengths = []
        self.wait_times = []
        self.timestamps = []

    def record_length(self, length, time):
        """Record queue length at given time"""
        self.queue_lengths.append(length)
        self.timestamps.append(time)

    def record_wait(self, wait_time):
        """Record a passenger's wait time"""
        self.wait_times.append(wait_time)

    @property
    def average_length(self):
        """Calculate average queue length"""
        return np.mean(self.queue_lengths) if self.queue_lengths else 0

    @property
    def average_wait(self):
        """Calculate average wait time"""
        return np.mean(self.wait_times) if self.wait_times else 0

    @property
    def max_length(self):
        """Get maximum queue length"""
        return max(self.queue_lengths) if self.queue_lengths else 0

    @property
    def max_wait(self):
        """Get maximum wait time"""
        return max(self.wait_times) if self.wait_times else 0
