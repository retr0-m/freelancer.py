"""
Instagram Social Media Manager
"""

import os
import time
import random
import pickle

import sys
sys.path.insert(1, '../')
from log import log

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()


class InstagramManager:
    # ----------------------------
    # CONFIG
    # ----------------------------
    BASE_URL = "https://www.instagram.com/"
    LOGIN_URL = "https://www.instagram.com/accounts/login/"
    COOKIE_FILE = "cookies.pkl"

    def __init__(self, username=None, password=None, timeout=20):
        log("→ __init__() start")
        self.username = username or os.getenv("IG_USERNAME")
        self.password = password or os.getenv("IG_PASSWORD")
        self.timeout = timeout

        self.driver = None
        self.wait = None
        log("← __init__() end")

    # ----------------------------
    # INTERNAL HELPERS
    # ----------------------------

    @staticmethod
    def human_sleep(a=1.5, b=3.5):
        time.sleep(random.uniform(a, b))

    @staticmethod
    def human_type(element, text, min_delay=0.05, max_delay=0.15):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))

    # ----------------------------
    # DRIVER MANAGEMENT
    # ----------------------------

    def create_driver(self):
        log("→ create_driver() start")

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--lang=en-US")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.timeout)

        log("← create_driver() end")
        return self.driver

    def quit(self):
        log("→ quit() start")
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
        log("← quit() end")

    # ----------------------------
    # COOKIES
    # ----------------------------

    def save_cookies(self):
        log("→ save_cookies() start")
        with open(self.COOKIE_FILE, "wb") as f:
            pickle.dump(self.driver.get_cookies(), f)
        log("← save_cookies() end")

    def load_cookies(self):
        log("→ load_cookies() start")

        if not os.path.exists(self.COOKIE_FILE):
            log("← load_cookies() end (no file)")
            return False

        with open(self.COOKIE_FILE, "rb") as f:
            cookies = pickle.load(f)

        self.driver.get(self.BASE_URL)
        for cookie in cookies:
            cookie.pop("sameSite", None)
            self.driver.add_cookie(cookie)

        self.driver.refresh()
        log("← load_cookies() end (loaded)")
        return True

    # ----------------------------
    # AUTH
    # ----------------------------

    def login(self):
        log("→ login() start")

        self.driver.get(self.BASE_URL)
        self.human_sleep()

        if self.load_cookies():
            log("🍪 Cookies loaded")
            self.human_sleep(3, 5)
            log("← login() end (cookies)")
            return

        log("🔐 Logging in manually")
        self.driver.get(self.LOGIN_URL)

        try:
            self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Allow')]")
                )
            ).click()
        except:
            pass

        username_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = self.driver.find_element(By.NAME, "password")

        for c in self.username:
            username_input.send_keys(c)
            time.sleep(random.uniform(0.05, 0.15))

        self.human_sleep()

        for c in self.password:
            password_input.send_keys(c)
            time.sleep(random.uniform(0.05, 0.15))

        password_input.send_keys(Keys.ENTER)

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href,'/direct/')]")
            )
        )

        self.save_cookies()
        log("✅ Logged in")
        log("← login() end")

    # ----------------------------
    # BUSINESS ACTIONS
    # ----------------------------
    def start_following(self):
        log("→ start_following() start")

        self.human_sleep(3, 5)

        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[text()='Follow' or text()='Follow Back']")
                )
            )
            btn.click()
            log(f"➕ Started following user")
        except:
            log(f"⚠️ Could not follow user (maybe already following?)")

        log("← start_following_user_by_username() end")

    def start_following_user_by_username(self, username):
        log("→ start_following_user_by_username() start")

        profile_url = f"{self.BASE_URL}{username}/"
        self.driver.get(profile_url)
        self.human_sleep(3, 5)

        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[text()='Follow' or text()='Follow Back']")
                )
            )
            btn.click()
            log(f"➕ Started following @{username}")
            self.human_sleep(3,5)
        except:
            log(f"⚠️ Could not follow @{username} (maybe already following?)")

        log("← start_following_user_by_username() end")

    def upload_file_to_dm(self, username, file_path):
        log("→ upload_file_to_dm() start")

        profile_url = f"{self.BASE_URL}{username}/"
        self.driver.get(profile_url)
        self.human_sleep(3, 5)

        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[text()='Message' or text()='Send message']")
                )
            )
            btn.click()
        except:
            log("← upload_file_to_dm() end (cannot open DM)")
            raise RuntimeError(f"Cannot message @{username}")

        self.human_sleep(3, 5)

        # Notification popup
        try:
            not_now = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
            )
            not_now.click()
            self.human_sleep()
        except:
            pass

        # Find file input (hidden)
        file_input = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='file']")
            )
        )

        # Force visible (important)
        self.driver.execute_script(
            "arguments[0].style.display = 'block';", file_input
        )

        file_input.send_keys(os.path.abspath(file_path))

        log(f"📤 File uploaded to DM with @{username}")
        log("← upload_file_to_dm() end")

    def open_user_dm(self, username):
        log("→ open_user_dm() start")

        profile_url = f"{self.BASE_URL}{username}/"
        self.driver.get(profile_url)
        self.human_sleep(3, 5)

        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[text()='Message' or text()='Send message']")
                )
            )
            btn.click()
            log("← open_user_dm() end")
        except:
            log("← open_user_dm() end (failed)")
            raise RuntimeError(f"Cannot message @{username}")
    def send_message_to_user(self, username, message):

        self.human_sleep(3, 5)

        try:
            not_now = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
            )
            not_now.click()
        except:
            pass

        box = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true']")
            )
        )

        self.human_type(box, message)
        box.send_keys(Keys.ENTER)

        log(f"📨 Message sent to @{username}")
        log("← send_message_to_user() end")

    def send_proposal_to_user_by_username(self, username):
        log("→ send_proposal_to_user_by_username() start")

        proposal = (
            "Hey! \n"
            "I came across your profile and wanted to reach out. "
            "Let me know if you'd be open to a quick chat."
        )
        self.send_message_to_user(username, proposal)

        log("← send_proposal_to_user_by_username() end")

    # ----------------------------
    # TEST / HEALTH CHECK
    # ----------------------------

    def test(self, test_username, dry_run=True):
        log("→ test() start")
        log(f"🧪 Testing DM flow @{test_username} | dry_run={dry_run}")

        self.driver.get(f"{self.BASE_URL}{test_username}/")
        self.human_sleep(3, 5)

        self.wait.until(EC.presence_of_element_located((By.XPATH, "//header")))

        btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[text()='Message' or text()='Send message']")
            )
        )

        if dry_run:
            log("🛑 Dry run OK")
            log("← test() end")
            return True

        btn.click()
        self.human_sleep()

        log("← test() end")
        return True