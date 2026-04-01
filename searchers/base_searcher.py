from abc import ABC, abstractmethod

class BaseSearcher(ABC):
    """
    Abstract base class for academic database searchers.
    Extend this class when adding new databases.
    """
    def __init__(self):
        self.results = []

    @abstractmethod
    def search(self, query: str, max_results: int = 2000):
        """
        Executes a search query on the database.
        """
        pass

    @abstractmethod
    def save_results(self, filename: str):
        """
        Saves the retrieved results to a file.
        """
        pass
