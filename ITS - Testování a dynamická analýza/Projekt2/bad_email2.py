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

class TestRegistration():
 
  def teardown_method(self, method):
        self.driver.quit()
  
  @When('Uživatel zadá do kolonky E-mail platnou, ale již obsazenou E-mailovu adresu')
  def test_registration(self):
        self.driver.get("http://mys01.fit.vutbr.cz:8019/index.php?route=account/register")
        self.driver.find_element(By.ID, "input-email").click()
        self.driver.find_element(By.ID, "input-email").send_keys("ahoj@seznam.cz")
        self.driver.find_element(By.XPATH, "//input[@name=\'agree\']").click()
        self.driver.find_element(By.XPATH, "//input[@value=\'Continue\']").click()

  @Then('Ukáže se zpráva "Warning: E-Mail Address is already registered!"')
  def alert(self):
        assert self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "Warning: E-Mail Address is already registered!"

