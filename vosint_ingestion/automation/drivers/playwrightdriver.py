import time

from playwright.sync_api import sync_playwright

from ..common import SelectorBy
from .basedriver import BaseDriver

class PlaywrightDriver(BaseDriver):
    def __init__(self,ip_proxy = None, port = None, username = None, password = None):
        if ip_proxy != None and port != None and username != None and password != None:
            proxy_server = {
                'server': ip_proxy,
                'port': port,
                'username': username,
                'password': password
            }
            self.playwright = sync_playwright().start()
            self.driver = self.playwright.chromium.launch(channel="chrome",
                                                          proxy={
                                                                'server': proxy_server['server'] + ':' + str(proxy_server['port']),
                                                                'username': proxy_server['username'],
                                                                'password': proxy_server['password']
                                                            })
            self.page = self.driver.new_page()

        else:

            self.playwright = sync_playwright().start()
            self.driver = self.playwright.chromium.launch(channel="chrome")
            self.page = self.driver.new_page()
        
    def get_driver(self):
        return self.driver
    
    def get_page(self):
        return self.page

    def destroy(self):
        self.driver.close()
        self.playwright.stop()

    def goto(self, url: str):
        self.page.goto(url)
        return self.page

    def select(self, from_elem, by: str, expr: str):
        by = self.__map_selector_by(by)
        elems = from_elem.locator(f"{by}{expr}")
        # Cast elems to list
        elems = [elems.nth(i) for i in range(elems.count())]
        return elems

    def get_attr(self, from_elem, attr_name: str):
        return from_elem.get_attribute(attr_name)

    def get_content(self, from_elem) -> str:
        return from_elem.inner_text()
    
    def get_html(self, from_elem) -> str:
        return from_elem.inner_html()    


    def click(self, from_elem, time_sleep = 0.3):
        from_elem.click()
        time.sleep(float(time_sleep))
        return self.page

    # TODO DoanCT: Bo sung scroll, sendkey
    def scroll(self, from_elem, value: int = 1, time_sleep: float=0.3):
        for i in range(value):  # make the range as long as needed
            from_elem.keyboard.press('End')
            from_elem.wait_for_selector('body')
            time.sleep(time_sleep)
        
        return from_elem

    # TODO DoanCT: Bo sung scroll, sendkey
    def scroll_page(self, value: int = 1, time_sleep: float=0.3):
        for i in range(value):  # make the range as long as needed
            self.page.keyboard.press('End')
            self.page.wait_for_selector('body')
            time.sleep(time_sleep)
        
        return self.page
    
    def sendkey(self, from_elem, value: str):
        return from_elem.type(value)

    def fill(self, from_elem, value: str):
        return from_elem.fill(value)

    def __map_selector_by(self, selector_by: str) -> str:
        return "xpath=" if selector_by == SelectorBy.XPATH else "css="
    
    def hover(self, from_elem):
        return from_elem[0].hover()
