from ssl import SSLError
import scpentry as scp
import requests
from bs4 import BeautifulSoup as bsoup, NavigableString, Tag
from threading import Thread, Lock

THREADS = 4
GLOBAL_ID_LOCK = Lock()
GLOBAL_NUM_LOCK = Lock()
GLOBAL_SET_LOCK = Lock()

def thread_set_contains_entry(url : str, set : set[scp.SCPEntry]) -> bool:
    for entry in set:
        if url == entry.get_url():
            return True
    return False

def thread_create_entry(id : list[int], url : str) -> scp.SCPEntry:
    title, links = grab(url)
    if not title is None:
        with GLOBAL_ID_LOCK:
            entry = scp.SCPEntry(id[0],title,url)
            id[0] += 1
        entry.add_links(links)
        return entry
    else:
        return None

def thread_get_free_entry(id : list[int], num : list[int], crawled : set[scp.SCPEntry], uncrawled : set[scp.SCPEntry], crawling : set[scp.SCPEntry]) -> scp.SCPEntry:
    with GLOBAL_NUM_LOCK:
        with GLOBAL_SET_LOCK:
            exists = True
            entry = None
            while exists:
                url = num_to_scp_page(num[0])
                exists = thread_set_contains_entry(url, crawled) or thread_set_contains_entry(url, uncrawled) or thread_set_contains_entry(url, crawling)
                if not exists:
                    entry = thread_create_entry(id, url)
                    if entry is None:
                        exists = True
                        continue
                    crawling.add(entry)
                    num[0] += 1
                    break
                num[0] += 1
                if num[0] > MAX_SCP:
                    return None
    return entry

def thread_entry_update_helper(entry : scp.SCPEntry, new_entry : scp.SCPEntry, set : set[scp.SCPEntry]) -> bool:
    if new_entry in set:
        for set_entry in set:
            if new_entry == set_entry:
                entry.add_reference(set_entry)
        return True
    return False

def thread_crawl_entry(id : list[int], entry : scp.SCPEntry, crawled : set[scp.SCPEntry], uncrawled : set[scp.SCPEntry], crawling : set[scp.SCPEntry]) -> None:
    with GLOBAL_SET_LOCK:
        if not entry in crawling:
            crawling.add(entry)
    for link in entry.get_links():
        new_entry = thread_create_entry(id, link)
        if new_entry is None:
            continue
        with GLOBAL_SET_LOCK:
            if thread_entry_update_helper(entry, new_entry, crawled):
                continue
            if thread_entry_update_helper(entry, new_entry, uncrawled):
                continue
            if thread_entry_update_helper(entry, new_entry, crawling):
                continue
            error = False
            for err in ERRORS:
                if err in new_entry.name:
                    error = True
                    break
            if not error:
                uncrawled.add(new_entry)
                entry.add_reference(new_entry)
                continue
            print(new_entry)
    with GLOBAL_SET_LOCK:
        crawling.remove(entry)
        crawled.add(entry)
    entry.clear_links()

def crawler_thread(id : list[int], num : list[int], crawled : set[scp.SCPEntry], uncrawled : set[scp.SCPEntry], crawling : set[scp.SCPEntry], exit : list[bool]) -> None:
    while True:
        current_entry : scp.SCPEntry = None
        with GLOBAL_SET_LOCK:
            if len(uncrawled) > 0:
                current_entry = uncrawled.pop()
        if current_entry is None:
            current_entry = thread_get_free_entry(id, num, crawled, uncrawled, crawling)
            if current_entry is None:
                return
        print(f'Crawling through entry #{current_entry.id()}: {current_entry}')
        thread_crawl_entry(id, current_entry, crawled, uncrawled, crawling)
        if exit[0]:
            return

def main():
    crawled = set()
    uncrawled = set()
    crawling = set()
    id = [0]
    num = [0]
    exit = [False]
    threads = []
    for _ in range(THREADS):
        thread = Thread(target=crawler_thread,args=(id,num,crawled,uncrawled,crawling,exit,))
        thread.start()
        threads.append(thread) 

if __name__ == '__main__':
    main()