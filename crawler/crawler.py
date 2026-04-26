from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("https://www.tiktok.com//search?q=La%20cha%F0%9F%8D%95")
title = driver.title
driver.implicitly_wait(15)
text_box = driver.find_element(by=By.TAG_NAME, value="html")
print(text_box.get_innerHTML("innerHTML"))
