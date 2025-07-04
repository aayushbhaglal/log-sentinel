from abc import ABC, abstractmethod

class LogSource(ABC):
    @abstractmethod
    def stream(self):
        """Yield log lines in real-time"""
        pass