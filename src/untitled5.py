import time
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# The account you want to check
account = "natoogram"



def login(driver):
    username = ""   # Your username
    password = ""   # Your password

    # Load page
    driver.get("https://www.instagram.com/accounts/login/")

    # Login
    driver.find_element_by_xpath("//div/input[@name='username']").send_keys(username)
    driver.find_element_by_xpath("//div/input[@name='password']").send_keys(password)
    driver.find_element_by_xpath("//span/button").click()

    # Wait for the login page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "See All")))


def scrape_followers(driver, account):
    # Load account page
    driver.get("https://www.instagram.com/{0}/".format(account))

    # Click the 'Follower(s)' link
    driver.find_element_by_partial_link_text("follower").click()

    # Wait for the followers modal to load
    xpath = "/html/body/div[3]/div/div"
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = 0.5  # Pause to allow loading of content
    driver.execute_script("var followersbox = document.getElementsByClassName('_gs38e')[0];")
    followers_box=driver.find_element_by_class_name('j6cq2')
    last_height=followers_box.get_attribute("scrollHeight")
    
    followers_list=driver.find_element_by_class_name('_1xe_U')
    followers=followers_list.find_elements_by_tag_name("li")


    # We need to scroll the followers modal to ensure that all followers are loaded
    while True:
        driver.execute_script("document.getElementsByClassName('j6cq2')[0].scrollTo(0, %s);" % last_height)

        # Wait for page to load
        time.sleep(0.1)

        # Calculate new scrollHeight and compare with the previous
        new_height = followers_box.get_attribute("scrollHeight")
#        if new_height == last_height:
#            break
        last_height = new_height
        followers=followers_list.find_elements_by_tag_name("li")
        print(len(followers))

    # Finally, scrape the followers
    xpath = "/html/body/div[4]/div/div/div[2]/div/div[2]/ul/li"
    followers_elems = driver.find_elements_by_xpath(xpath)
    followers_temp = [e.text for e in followers_elems]  # List of followers (username, full name, follow text)
    followers = []  # List of followers (usernames only)

    # Go through each entry in the list, append the username to the followers list
    for i in followers_temp:
        username, sep, name = i.partition('\n')
        followers.append(username)

    print("______________________________________")
    print("FOLLOWERS")

    return followers


if __name__ == "__main__":

    driver = wd.Firefox()
    try:
        login(driver)
        followers = scrape_followers(driver, account)
        print(followers)

    finally:
        driver.quit()
        
var="uilbuilbuil"
l=[]
for i in range(0,500000):
   l.append(1000000000000+i) 