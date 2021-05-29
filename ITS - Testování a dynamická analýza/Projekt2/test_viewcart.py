import pytest
from behave import *
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestViewcart():

    @Given("Uživatel je na jakékoliv stránce E-shopu")
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
  
    
    @When('Uživatel klikne na velké černé tlačítko v pravé horní části')
    @When('v košíku se nachází alespoň 1 produkt')
    # aby sel zobrazit kosik musime pridat aspon 1 polozku
    def add(self):
        self.driver.get("http://mys01.fit.vutbr.cz:8019/")
        self.driver.find_element(By.XPATH, "//div[@id=\'content\']/div[2]/div[4]/div/div[3]/button").click()
        self.driver.find_element(By.XPATH, "//select[@id=\'input-option226\']").click()
        self.driver.find_element(By.XPATH, "//div[@id=\'product\']/div/select").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(2)").click()
        self.driver.find_element(By.ID, "input-option226").click()
        self.driver.find_element(By.ID, "button-cart").click()

    @When('klikne na tlačítko "View Cart"')
    def click_view_cart(self):
        self.driver.execute_script("window.scrollTo(0,94)")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-inverse").click()
        self.driver.find_element(By.CSS_SELECTOR, "a:nth-child(1) > strong").click()

    @Then('Zobrazí se obsah nákupního košíku.')
    def is_elem(self):
        elements = self.driver.find_elements(By.LINK_TEXT, "Shopping Cart")
        assert len(elements) > 0
  
