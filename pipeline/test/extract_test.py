from unittest import main
from extract import extract

if __name__ == "__main__":
    extract_obj = extract("../dataset/tiktok/7533282684521450760.html")
    user_comments = extract_obj.traverse_comments()
    # for user in user_comments:
    #    print(user_comments)
