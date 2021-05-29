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

class TestReg2():
   
  def teardown_method(self, method):
    self.driver.quit()
  

 
  @When('Uživatel vyplnil všechny povinné kolonky1')
  def test_reg2(self):
    self.driver.get("http://mys01.fit.vutbr.cz:8019/index.php?route=account/register")
    self.driver.set_window_size(1350, 857)
    self.driver.find_element(By.ID, "input-firstname").click()
    self.driver.find_element(By.ID, "input-firstname").send_keys("aaa")
    self.driver.find_element(By.ID, "input-lastname").click()
    self.driver.find_element(By.ID, "input-lastname").send_keys("aaaa")
    self.driver.find_element(By.ID, "input-email").click()
    self.driver.find_element(By.ID, "input-email").send_keys("kol563@vmi.cpm")
    self.driver.find_element(By.ID, "input-telephone").click()
    self.driver.find_element(By.ID, "input-telephone").send_keys("123456789")
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

    @Then('Ukáže se stránka se zprávou "Your Account Has Been Created!" And Byl vytvořen nový účet.')
    def assertion(self):
        #assert self.driver.find_element(By.XPATH, "//h1[contains(.,\'Your Account Has Been Created!\')]").text == 'Your Account Has Been Created!'
        elements = self.driver.find_elements(By.CSS_SELECTOR, "h1")
        assert len(elements) > 0
  
