class Crawler:
    """
    A crawler for scp-wiki.wikidot.com

    Crawler is threaded by default.
    """

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

