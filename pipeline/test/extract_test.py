from unittest import main
from extract import extract

if __name__ == "__main__":
    # Maligno "7533282684521450760.html"
    # Benigno "7629140208386116885.html"
    extract_obj = extract("../dataset/tiktok/7630679434005204245.html")
    user_comments = extract_obj.traverse_comments()
    # for user in user_comments:
    #    print(user_comments)
