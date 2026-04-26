from unittest import main
from scrapper import scrapper

if __name__ == "__main__":
    scrapper_obj = scrapper("../dataset/tiktok/index.html")
    users_videos = scrapper_obj.get_all_username()
    print(users_videos)
