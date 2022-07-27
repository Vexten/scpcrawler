from threading import Lock

class SafeWrapper:
    """
    Makes calls to contained object thread-safe
    """
    def __init__(self, obj) -> None:
        self.__lock = Lock()
        self.__obj = obj
    
    def __locker(self, func):
        """
        Locking wrapper for calls to object
        """
        def wrapper(*args, **kwargs):
            with self.__lock:
                result = func(*args, **kwargs)
            return result
        
        return wrapper

    def __getattr__(self, __attr):
        """
        Pass wrapper calls to __obj
        """
        return self.__locker(getattr(self.__obj, __attr))
    
    def __repr__(self) -> str:
        return self.__obj.__repr__()

    def __str__(self) -> str:
        return self.__obj.__str__()


class EntryStorage:
    """
    Provides thread-safe storage for entries.
    """
