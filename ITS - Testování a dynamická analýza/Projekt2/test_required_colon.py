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

class TestReg2():

  @Given('Uživatel má před sebou stránku s registračním formulářem.')
  def setup_method(self):
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
  

  @When('Uživatel nevyplnil kolonku s povinnými údaji')
  def test_reg2(self):
    self.driver.get("http://mys01.fit.vutbr.cz:8019/index.php?route=account/register")
    self.driver.set_window_size(1350, 857)
    self.driver.find_element(By.ID, "input-firstname").click()
    self.driver.find_element(By.ID, "input-firstname").send_keys("aaa")
    self.driver.find_element(By.ID, "input-lastname").click()
    self.driver.find_element(By.ID, "input-lastname").send_keys("aaaa")
    self.driver.find_element(By.ID, "input-email").click()
    self.driver.find_element(By.ID, "input-email").send_keys("kol3@vm.cpm")
    self.driver.find_element(By.ID, "input-telephone").click()
    self.driver.find_element(By.ID, "input-address-1").click()
    self.driver.find_element(By.ID, "input-address-1").send_keys("sss")
    self.driver.find_element(By.ID, "input-address-2").click()
    self.driver.find_element(By.ID, "input-city").click()
    self.driver.find_element(By.ID, "input-city").send_keys("rrrr")
    self.driver.find_element(By.ID, "input-postcode").click()
    self.driver.find_element(By.ID, "input-postcode").click()
    self.driver.find_element(By.ID, "input-country").click()
    dropdown = self.driver.find_element(By.ID, "input-country")
    dropdown.find_element(By.XPATH, "//option[. = 'Switzerland']").click()
    self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(220)").click()
    self.driver.execute_script("window.scrollTo(0,408)")
    self.driver.find_element(By.ID, "input-zone").click()
    dropdown = self.driver.find_element(By.ID, "input-zone")
    dropdown.find_element(By.XPATH, "//option[. = 'Glarus']").click()
    self.driver.find_element(By.CSS_SELECTOR, "#input-zone > option:nth-child(10)").click()
    self.driver.find_element(By.ID, "input-password").click()
    self.driver.find_element(By.ID, "input-password").send_keys("12345")
    self.driver.find_element(By.ID, "input-confirm").click()
    self.driver.find_element(By.ID, "input-confirm").send_keys("12345")
    self.driver.find_element(By.NAME, "agree").click()

    @When('klikne na tlačítko continue.')
    def click(self):
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

    @Then('Ukáže se varovná zpráva')
    def assertion(self):
        assert self.driver.find_element(By.CSS_SELECTOR, ".text-danger").text == "Telephone must be between 3 and 32 characters!"
