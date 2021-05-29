import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os


class TestCompleteorder():
  
    @Given('Uživatel je na stránce "Shopping Cart"')
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
  
    @When('Uživatel klikne na tlačítko "Checkout"')
    def test_completeorder(self):
        self.driver.get("http://mys01.fit.vutbr.cz:8019/index.php?route=product/product&product_id=30")
        self.driver.find_element(By.ID, "input-option226").click()
        self.driver.find_element(By.XPATH, "//div[@id=\'product\']/div/select").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(2)").click()
        self.driver.find_element(By.ID, "button-cart").click()
        self.driver.execute_script("window.scrollTo(0,94)")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-inverse").click()
        self.driver.find_element(By.CSS_SELECTOR, "a:nth-child(1) > strong").click()
        self.driver.find_element(By.XPATH, "//a[contains(text(),\'Checkout\')]").click()
        self.driver.find_element(By.CSS_SELECTOR, ".radio:nth-child(4) > label").click()
        self.driver.find_element(By.XPATH, "//input[@id=\'button-account\']").click()

    @When('Vyplní sekci "Billing details"')
    def details(self):
        self.driver.find_element(By.ID, "input-payment-firstname").click()
        self.driver.find_element(By.ID, "input-payment-firstname").send_keys("aaa")
        self.driver.find_element(By.ID, "input-payment-lastname").click()
        self.driver.find_element(By.ID, "input-payment-lastname").send_keys("aaaa")
        self.driver.find_element(By.ID, "input-payment-email").click()
        self.driver.find_element(By.ID, "input-payment-email").send_keys("tio@kol.vm")
        self.driver.find_element(By.ID, "input-payment-telephone").click()
        self.driver.find_element(By.ID, "input-payment-telephone").send_keys("123456789")
        self.driver.find_element(By.ID, "input-payment-address-1").click()
        self.driver.find_element(By.ID, "input-payment-address-1").send_keys("llll")
        self.driver.find_element(By.ID, "input-payment-address-2").click()
        self.driver.find_element(By.ID, "input-payment-city").click()
        self.driver.find_element(By.ID, "input-payment-city").send_keys("kkkkk")
        self.driver.find_element(By.ID, "input-payment-postcode").click()
        self.driver.find_element(By.ID, "input-payment-postcode").send_keys("456")
        self.driver.find_element(By.ID, "input-payment-country").click()
        dropdown = self.driver.find_element(By.ID, "input-payment-country")
        dropdown.find_element(By.XPATH, "//option[. = 'Tonga']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(228)").click()
        self.driver.find_element(By.ID, "input-payment-zone").click()
        dropdown = self.driver.find_element(By.ID, "input-payment-zone")
        dropdown.find_element(By.XPATH, "//option[. = 'Tongatapu']").click()
        self.driver.find_element(By.CSS_SELECTOR, "#input-payment-zone > option:nth-child(3)").click()
       
       
    
    @When('Vyplní sekci "Payment method"')
    @When('Klikne na tlačítko "Confirm Order"')
    def payment(self):
        self.driver.find_element(By.XPATH, "//div[3]/div/input").click()
        self.driver.execute_script("window.scrollTo(0,510)")
        self.driver.find_element(By.XPATH, "//input[@id=\'button-shipping-method\']").click()
        wait = WebDriverWait(self.driver, 5)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name=\'agree\']')))
        self.driver.find_element(By.XPATH, "//input[@name=\'agree\']").click()
        self.driver.find_element(By.ID, "button-payment-method").click()
        self.driver.find_element(By.ID, "button-confirm").click()


    @Then('Zobrazí se zpráva "Your order has been placed!"')
    def assertion(self):
        assert self.driver.find_element(By.XPATH, "//h1[contains(.,\'Your order has been placed!\')]").text == "Your order has been placed!"
  
