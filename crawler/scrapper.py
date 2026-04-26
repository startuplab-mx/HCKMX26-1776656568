from bs4 import BeautifulSoup
import re


class scrapper:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.file_ptr = open(filename, "r")
        self.file_content = self.file_ptr.read()
        self.html_code = BeautifulSoup(self.file_content, "html.parser")
        pass

    def get_all_username(self):
        users = {}
        for link in self.html_code.find_all("a"):
            text = link.get("href")
            user_name_match_obj = re.search(r"@([^/]+)/", text)
            user_video_match_obj = re.search(r"/video/(\d+)", text)
            if user_name_match_obj != None and user_video_match_obj != None:
                user_name = user_name_match_obj.group(1)
                user_video = user_video_match_obj.group(1)
                if user_name not in users:
                    list = []
                    print(user_video)
                    list.append(user_video)
                    users[user_name] = list
                else:
                    users[user_name] = users[user_name].append(user_video)
        return users

    def generate_search_tree
