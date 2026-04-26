from bs4 import BeautifulSoup
from pathlib import Path
import re


class extract:
    def __init__(self, filename) -> None:
        self.filename = filename

        self.file_content = Path(filename).read_text(encoding="utf-8")
        self.html_code = BeautifulSoup(self.file_content, "html.parser")

    def traverse_comments(self):
        users = {}
        html_pretty = self.html_code.prettify()
        # print(html_pretty)
        html_pretty = BeautifulSoup(html_pretty, "html.parser")
        username_widget_html = html_pretty.find_all(
            attrs={"data-e2e": "comment-username-1"}
        )
        user_comment_widget_html = html_pretty.find_all(
            attrs={"data-e2e": "comment-level-1"}
        )

        for div in username_widget_html:
            for href in div.find_all("a"):
                # print(f"Objeto {div.find_all('a')}")
                print(href.get("href")[1:])

        for div in user_comment_widget_html:
            # print(f"Objeto {div.find_all('span')}")
            print("Objeto")
            for comment in div.find_all("span"):
                texto = " ".join(comment.getText("").split())
                print(texto)
