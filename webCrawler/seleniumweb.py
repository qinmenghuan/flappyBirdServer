from selenium import webdriver
from time import sleep
# driver = webdriver.Firefox()
driver = webdriver.Chrome()
driver.get("http://www.baidu.com")
print('设置浏览器全屏打开')
driver.maximize_window()
# driver.find_element_by_xpath(".//*[@id='kw']").send_keys("python")
# driver.find_element_by_xpath(".//*[@id='su']").click()
location = driver.find_element_by_xpath("//div[@id='u1'p /]/a[3]").location
print (location)
sleep(5)
# driver.quit()
