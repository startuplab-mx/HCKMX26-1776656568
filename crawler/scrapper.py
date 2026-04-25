from bs4 import BeautifulSoup


class scrapper:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.html_code = BeautifulSoup(filename, "html.parser")
        pass

    def get_all_username():
        user = set()
        for link in soup.find_all("a"):
            print(link.get("href"))
