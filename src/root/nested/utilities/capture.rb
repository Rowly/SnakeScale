require 'selenium-webdriver'
require 'headless'

target = ARGV[0]

headless = Headless.new
headless.start

driver = Selenium::WebDriver.for :firefox
wait = Selenium::WebDriver::Wait.new(:timeout => 60)

driver.navigate.to target

def wait_for_clickable_element(locator)
  element = wait.until { driver.find_element(locator) }
  wait.until { element.displayed? }
  wait.until { element.enabled? }
  return element
end

element = wait_for_clickable_element(:css => "#refresh_thumbnail")
element.click

element = wait_for_clickable_element(:css => "#right > div > a:nth-child(5)")
element.click

driver.save_screenshot("../imgs/capture.png")

headless.destroy
