from html.parser import HTMLParser

class LinkParser(HTMLParser):
    """ DOM parser to retrieve href of all <a> elements """

    def parse_links(self, html_content):
        self.links = []
        try:
            self.feed(html_content)
        except NotImplementedError:
            pass
        return self.links

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = {key.lower():value for key, *value in attrs}
            urls = attrs.get("href", None)
            if urls and urls[0]:
                self.links.append(urls[0])
