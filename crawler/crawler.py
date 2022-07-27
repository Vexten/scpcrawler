from bs4 import BeautifulSoup as bsoup, Tag, NavigableString
import requests
from ssl import SSLError

SCP_WIKI = 'http://scp-wiki.wikidot.com'
SCP_WIKI_HTTPS = 'https://scp-wiki.wikidot.com'
SCP_PREFIX = '/scp-'
CONTENT_ID = 'page-content'
FOOTER_CLASS = 'footer-wikiwalk-nav'
LICENSE_CLASS = 'licensebox'
TAGS_CLASS = 'page-tags'
FORBIDDEN_TAGS = ['hub','admin','author','component','essay','resource','guide']
TITLE_WIKI = ' - SCP Foundation'
MAX_SCP_NAME_LEN = 9
MAX_SCP = 6999
ENTRY_CONNECTION_ERROR = 'CONNECTION_ERROR'
ERRORS = [ENTRY_CONNECTION_ERROR]

class Crawler:
    """
    A crawler for scp-wiki.wikidot.com

    Crawler is threaded by default.
    """

    @classmethod
    def int_to_scp_code(num : int) -> str:
        snum = str(num)
        snum = '0'*(3-len(snum)) + snum
        return snum
    
    @classmethod
    def int_to_scp_page_url(num : int) -> str:
        return SCP_WIKI + SCP_PREFIX + Crawler.int_to_scp_code(num)

    @classmethod
    def get_content(soup : bsoup) -> Tag | NavigableString:
        content = soup.find('div', id=CONTENT_ID)
        footer = content.find('div', class_=FOOTER_CLASS)
        if not footer is None:
            footer.decompose()
        license = content.find('div', class_=LICENSE_CLASS)
        if not license is None:
            license.decompose()
        return content

    @classmethod
    def filter_links(link_list : list, link_set : set) -> None:
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

    @classmethod
    def page_is_an_entry(soup : bsoup) -> bool:
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

    @classmethod
    def get_title_and_links(url : str) -> tuple[str,set]:
        retries = 0
        resp = None
        links = set()
        while True:
            if retries > 2:
                return url.replace(SCP_WIKI + '/','').capitalize() + ': ' + ENTRY_CONNECTION_ERROR, links
            try:
                resp = requests.get(url)
                if not resp is None:
                    break
            except SSLError:
                retries += 1
        soup = bsoup(resp.text, 'html.parser')
        if Crawler.page_is_an_entry(soup):
            title = soup.title.string.replace(TITLE_WIKI,'')
            content = Crawler.get_content(soup)
            links_list = [a['href'] for a in content.find_all(href=True)]
            Crawler.filter_links(links_list,links)
            return title, links
        else:
            return None, None
