class SCPEntry:
    def __init__(self, id, name, url = None) -> None:
        self.__id = id
        self.name = name
        self.url = url
        self.__contained_urls = set()
        self.__references = set()
        self.__referenced_by = set()
        self.__ref_counter = 0

    def add_reference(self, SCPEntry) -> None:
        if not (SCPEntry in self.__references):
            SCPEntry.__ref_counter += 1
            SCPEntry.__referenced_by.add(self)
            self.__references.add(SCPEntry)
    
    def add_links(self, links) -> None:
        for link in links:
            self.__contained_urls.add(link)

    def has_url(self) -> bool:
        return not self.url is None

    def get_url(self) -> str:
        return self.url

    def get_links(self) -> list:
        return self.__contained_urls
    
    def clear_links(self) -> None:
        self.__contained_urls.clear()

    def referenced_by(self) -> str:
        return "Referenced by:\n" + str(self.__referenced_by).replace(', ','\n')[1:-1] + "\nIn total referenced " + str(self.__ref_counter) + " times.\n"

    def references(self) -> str:
        return 'References:\n' + str(self.__references).replace(', ','\n')[1:-1] + "\n"

    def __repr__(self) -> str:
        if not self.name is None:
            return self.name
        return self.url

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, __o: object) -> bool:
        if type(__o) is SCPEntry:
            return self.name == __o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    def id(self) -> int:
        return self.__id
