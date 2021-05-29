import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestAddtocart():
    @Given("Uživatel je na stránce s nabídkou produktů.")
    def setUp(self):
        dp = {'browserName': 'firefox', 'marionette': 'true',
                'javascriptEnabled': 'true'}
        self.driver = webdriver.Remote(
        command_executor='http://mys01.fit.vutbr.cz:4444/wd/hub',
        desired_capabilities=dp)
        #desired_capabilities=DesiredCapabilities.FIREFOX)
        self.driver.implicitly_wait(15)
        self.base_url = "http://mys01.fit.vutbr.cz:8019/"
        self.verificationErrors = []
        self.accept_next_alert = True
  
    def teardown_method(self, method):
        self.driver.quit()
  
    @When('Uživatel klikne na tlačítko "ADD TO CART"')
    def test_addtocart(self):
        self.driver.get("http://mys01.fit.vutbr.cz:8019/")
        self.driver.find_element(By.XPATH, "//div[@id=\'content\']/div[2]/div[4]/div/div[3]/button").click()
        self.driver.find_element(By.XPATH, "//select[@id=\'input-option226\']").click()
        self.driver.find_element(By.XPATH, "//div[@id=\'product\']/div/select").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(2)").click()
        self.driver.find_element(By.ID, "input-option226").click()
        self.driver.find_element(By.ID, "button-cart").click()

    @Then('Příslušný produkt byl přidán do košíku.')
    def end(self):
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert")
        assert len(elements) > 0
  
