from ssl import SSLError
import scpentry as scp
import requests
from bs4 import BeautifulSoup as bsoup, NavigableString, Tag
from threading import Thread, Lock

SCP_WIKI = 'http://scp-wiki.wikidot.com'
SCP_WIKI_HTTPS = 'https://scp-wiki.wikidot.com'
SCP_PREFIX = '/scp-'
CONTENT_ID = 'page-content'
FOOTER_CLASS = 'footer-wikiwalk-nav'
LICENSE_CLASS = 'licensebox'
TAGS_CLASS = 'page-tags'
FORBIDDEN_TAGS = ['hub','admin','author','component','essay']
TITLE_WIKI = ' - SCP Foundation'
MAX_SCP_NAME_LEN = 9
MAX_SCP = 6999
ENTRY_CONNECTION_ERROR = 'CONNECTION_ERROR'
ERRORS = [ENTRY_CONNECTION_ERROR]

THREADS = 4
GLOBAL_ID_LOCK = Lock()
GLOBAL_NUM_LOCK = Lock()
GLOBAL_SET_LOCK = Lock()

def num_to_scp_code(num : int) -> str:
    snum = str(num)
    snum = '0'*(3-len(snum)) + snum
    return snum

def num_to_scp_page(num : int) -> str:
    return SCP_WIKI + SCP_PREFIX + num_to_scp_code(num)

def get_content(soup : bsoup) -> Tag | NavigableString:
    content = soup.find('div', id=CONTENT_ID)
    footer = content.find('div', class_=FOOTER_CLASS)
    if not footer is None:
        footer.decompose()
    license = content.find('div', class_=LICENSE_CLASS)
    if not license is None:
        license.decompose()
    return content

def parse_links(link_list : list, link_set : set) -> None:
    for link in link_list:
        if not 'javascript' in link:
            if ('http' in link) and not (SCP_WIKI in link or SCP_WIKI_HTTPS in link):
                continue
            link = link.replace(SCP_WIKI_HTTPS,SCP_WIKI)
            if not SCP_WIKI in link:
                link = SCP_WIKI + link
            params = link.find('?')
            if not params == -1:
                link = link[0:params]
            link_set.add(link)

def is_entry(soup : bsoup) -> bool:
    tags_div = soup.find('div', class_=TAGS_CLASS)
    if tags_div is None:
        return False
    tags_div = tags_div.find_all('a')
    tags = []
    for tag in tags_div:
        tags.append(tag.text)
    ret = True
    for tag in FORBIDDEN_TAGS:
        if tag in tags:
            ret = False
            break
    return ret

def grab(url : str) -> tuple[str,set]:
    retries = 0
    resp = None
    links = set()
    while retries < 3:
        try:
            resp = requests.get(url)
            if not resp is None:
                break
        except SSLError:
            retries += 1
    if retries > 2:
        return url.replace(SCP_WIKI + '/','').capitalize() + ': ' + ENTRY_CONNECTION_ERROR, links
    soup = bsoup(resp.text, 'html.parser')
    if is_entry(soup):
        title = soup.title.string.replace(TITLE_WIKI,'')
        content = get_content(soup)
        links_list = [a['href'] for a in content.find_all(href=True)]
        parse_links(links_list,links)
        return title, links
    else:
        return None, None

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