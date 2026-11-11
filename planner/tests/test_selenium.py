"""
CS50 Week 7 – Selenium browser test.

Simulates a real user in headless Chrome:
login page -> log in -> add-task page -> save -> task appears on the page.

Requires Google Chrome installed. If no browser/driver can be started the test
is SKIPPED (not failed), so `python manage.py test` still works on any machine.
"""
import unittest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from .helpers import make_user

try:
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError:  # pragma: no cover
    webdriver = None


class StudyPlannerBrowserTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = None
        if webdriver is None:
            return
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")
        try:
            cls.driver = webdriver.Chrome(options=options)
        except WebDriverException:
            cls.driver = None

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        if self.driver is None:
            raise unittest.SkipTest("Chrome / Selenium driver is not available on this machine")
        make_user("selenium_user", "StrongPass123!")

    def wait(self):
        return WebDriverWait(self.driver, 10)

    def test_login_add_task_and_see_it(self):
        d = self.driver
        d.get(self.live_server_url + reverse("login"))                         # 1-2. open + login page
        d.find_element(By.NAME, "username").send_keys("selenium_user")         # 3. credentials
        d.find_element(By.NAME, "password").send_keys("StrongPass123!")
        d.find_element(By.CSS_SELECTOR, "button[type=submit]").click()         # 4. log in
        self.wait().until(EC.url_to_be(self.live_server_url + reverse("dashboard")))

        d.get(self.live_server_url + reverse("task_add"))                      # 5. creation page
        d.find_element(By.NAME, "title").send_keys("Revise CS50 Week 7")       # 6. add a task
        d.find_element(By.NAME, "description").send_keys("Testing and CI/CD")
        d.execute_script("document.getElementsByName('due_date')[0].value = '2030-01-01';")
        d.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()

        self.wait().until(EC.url_to_be(self.live_server_url + reverse("task_list")))
        self.assertIn("Revise CS50 Week 7", d.find_element(By.TAG_NAME, "body").text)  # 7. verify
