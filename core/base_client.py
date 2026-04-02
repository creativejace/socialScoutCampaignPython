from abc import ABC, abstractmethod

class BasePlatformClient(ABC):
    def __init__(self, access_token):
        self.access_token = access_token

    @abstractmethod
    def get_stats(self,video_id:str):
        raise NotImplementedError("This method should be overridden by subclasses.")