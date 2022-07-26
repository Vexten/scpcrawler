from types import MappingProxyType

class SCPEntry:
    """
    Represents an entry (SCP, tale, document) from scp-wiki.

    __hash__ and __eq__ defined using entry name, since
    entries with the same name should be the same entry
    """
    def __init__(self, id : int, name : str, url : str) -> None:
        self.__id : int = id
        self.__name : str = name
        self.__url : str = url
        self.__contained_urls : set[str] = set()
        self.__references : dict[str,'SCPEntry'] = dict()
        self.__referenced_by : dict[str,'SCPEntry'] = dict()
        self.__ref_counter : int = 0

    def add_reference(self, entry : 'SCPEntry') -> None:
        if not (entry in self.__references):
            entry.__ref_counter += 1
            entry.__referenced_by[str(self)] = self
            self.__references[str(entry)] = entry
    
    def add_links(self, links) -> None:
        """
        After crawling through an entry call :func:`clear_links()`
        """
        for link in links:
            self.__contained_urls.add(link)

    def name(self) -> str:
        return self.__name

    def url(self) -> str:
        return self.__url

    def links(self) -> list[str]:
        return self.__contained_urls
    
    def clear_links(self) -> None:
        """
        Always do after crawling through entry
        """
        self.__contained_urls.clear()

    def referenced_by_str(self) -> str:
        """
        Returns a formatted string that contains all entries that reference this one
        """
        return "Referenced by:\n" + str(list(self.__referenced_by.keys())).replace(', ','\n').replace("'",'')[1:-1] + "\nIn total referenced " + str(self.__ref_counter) + " times.\n"

    def references_str(self) -> str:
        """
        Returns a formatted string that contains all entries that this one references
        """
        return 'References:\n' + str(list(self.__references.keys())).replace(', ','\n').replace("'",'')[1:-1] + "\n"

    def referenced_by(self) -> MappingProxyType[str,'SCPEntry']:
        """
        Returns an immutable dict that contains all entries that reference this one
        """
        return MappingProxyType(self.__referenced_by)

    def referenced_by(self) -> MappingProxyType[str,'SCPEntry']:
        """
        Returns an immutable dict that contains all entries that this one references
        """
        return MappingProxyType(self.__references)

    def __repr__(self) -> str:
        if not self.__name is None:
            return self.__name
        return self.__url

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, __o: object) -> bool:
        if type(__o) is SCPEntry:
            return self.__name == __o.__name
        return False

    def __hash__(self) -> int:
        return hash(self.__name)

    def id(self) -> int:
        return self.__id
