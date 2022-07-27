from operator import getitem, setitem
from threading import Lock

class SafeIterator:
    """
    Thread-safe iterator wrapper implementation.
    
    !LOCKS UNDERLYING OBJECT UNTIL ITERATOR REACHES IT'S END!

    Requires an outside lock-type object.
    """
    def __init__(self, obj, lock : Lock) -> None:
        self.__obj = obj
        self.__lock : Lock = lock
        self.__locked = False
    
    def __iter__(self) -> 'SafeIterator':
        return self

    def __next__(self):
        if not self.__locked:
            self.__lock.acquire()
            self.__iterator = iter(self.__obj)
            self.__locked = True
        try:
            return next(self.__iterator)
        except StopIteration:
            del self.__iterator
            self.__locked = False
            self.__lock.release()
            raise StopIteration


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

    def __setitem__(self, __key, __val):
        """
        Item assignment support (self[__key] = __val)
        """
        self.__locker(setitem(self.__obj, __key, __val))

    def __getitem__(self, __key):
        """
        Item retrieval support (var = self[__key]) 
        """
        return self.__locker(getitem(self.__obj, __key))

    def __deleter(self, key):
        del self.__obj[key]

    def __delitem__(self, __key):
        """
        `del` operator
        """
        self.__locker(self.__deleter(__key))

    def __len__(self):
        """
        `len()` support
        """
        return self.__locker(len(self.__obj))

    def __iter__(self) -> SafeIterator:
        return SafeIterator(self.__obj, self.__lock)

    def __eq__(self, __o: object) -> bool:
        """
        Pass == to obj
        """
        return self.__locker(self.__obj.__eq__(__o))

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
