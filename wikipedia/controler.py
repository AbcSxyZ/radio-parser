from .page import PageInfo
from .wiki_error import PageError, PageNotExists
import logging
import sys

logger = logging.getLogger("wiki")

class SearchControler:
    def __init__(self, base_title):
        self.base_title = base_title

    def launch(self):
        page = PageInfo(self.base_title)
        # print(page.tables_by_section)
        
        for radios_table in page.tables:
            for radio in radios_table:
                if radio.have_wiki:
                    print("{} -> ".format(radio), end="")
                    sys.stdin.flush()
                    try:
                        page = PageInfo(str(radio), silent=True)
                    except (PageError, PageNotExists) as Error:
                        logger.warning(Error)
                        print()
                        continue
                    if page.type == PageInfo.RADIO:
                        print(page.radio_site)
                # try:
                # if radio.have_wiki:
                #     # print(radio)
                #     pass
                # except Exception as Error:
                #     import code
                #     code.interact(local=locals())
