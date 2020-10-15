'''Instagram WebScraping'''

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from time import sleep
import re

# TODO SCRAPING PROFILES DONE
# TODO SELENIUM WAIT
# TODO EXCEPT ATTR ERROR
# TODO CHANGE SEARCHING BY HASHTAG (by URL) DONE


class Cliker:
    def __init__(self, hashtags, private_only: False, business_only: False, email_only: False, proxy_port: None,
                proxy_host: ''):
        self.business_only = business_only
        self.private_only = private_only
        self.email_only = email_only
        self.hashtags = hashtags

        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        if proxy_host != '' and proxy_port != None:
            proxy = '{}:{}'.format(proxy_host, proxy_port)
            firefox_capabilities['proxy'] = {
                "proxyType": ProxyType.MANUAL,
                "httpProxy": proxy,
                "ftpProxy": proxy,
                "sslProxy": proxy
            }

        self.options = webdriver.FirefoxOptions()
        self.options.add_argument('--lang=en')
        self.options.add_argument('--start-maximized')
        try:
            self.driver = webdriver.Firefox(capabilities=firefox_capabilities, options=self.options)
        except InvalidArgumentException:
            print('Close Firefox and try again')

        self.driver.get('https://www.instagram.com/')
        sleep(2)

    def login(self, phone, password):
        phone_field = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
        password_field = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
        phone_field.send_keys(phone)
        password_field.send_keys(password)
        login = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div')
        login.click()

    def find_by_hashtag(self, hashtag):
        sleep(4)
        self.driver.get('https://www.instagram.com/explore/tags/{}/'.format(hashtag))

    def scroll_quantity(self, soup):
        try:
            quantity = soup.find('span', 'g47SY').string
            quantity = quantity.replace(',', '')

            return int(quantity) // 4

        except AttributeError:
            print('Scroll Quantity Not Found')
            return 300

    def click_photos(self):
        sleep(2)
        coord = 2000
        self.driver.execute_script("window.scrollTo(0, {})".format(coord))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        lines = soup.find_all('div', 'Nnq7C')
        for line in lines:
            photos = line.findChildren('div', 'v1Nh3')
            print(len(photos))
            for photo in photos:
                photo = self.driver.find_element_by_xpath(xpath_soup(photo))
                photo.click()
                self.click_profile()

        for _ in range(self.scroll_quantity(soup)):
            coord += 1150
            self.driver.execute_script("window.scrollTo(0, {})".format(coord))
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            lines = soup.find_all('div', 'Nnq7C')
            for line in lines[-4:]:
                photos = line.findChildren('div', 'v1Nh3')
                print(len(photos))
                for photo in photos:
                    photo = self.driver.find_element_by_xpath(xpath_soup(photo))
                    photo.click()
                    self.click_profile()

    def click_profile(self):
        sleep(0.5)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        profile_xpath = xpath_soup(soup.find('a', 'yWX7d'))
        self.driver.find_element_by_xpath(profile_xpath).click()
        sleep(1)
        scraper = Scraper(self.hashtags, self.private_only, self.business_only, self.email_only, None, '')
        scraper.scrape_profile()


class Scraper(Cliker):

    def has_email(self, soup):
        sleep(1)
        try:
            div = soup.find('div', '-vDIg')
            description = div.findChild('span').string
            email = re.findall(r'.+@.+\..+', description)
            if len(email) > 0:
                return True
            else:
                return False

        except AttributeError:
            return False



    def scrape_profile(self):
        sleep(1)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        if self.email_only:
            if self.has_email(soup):
                username = self.scrape_username(soup)
                posts = self.scrape_posts(soup)
                subscribed_on_your_profile = self.subscribed_on_you(soup)
                following = self.you_subscrided(soup)
                followers = self.scrape_subscribers(soup)
                name = self.scrape_name(soup)
        else:
            username = self.scrape_username(soup)
            posts = self.scrape_posts(soup)
            subscribed_on_your_profile = self.subscribed_on_you(soup)
            following =  self.you_subscrided(soup)
            followers = self.scrape_subscribers(soup)
            name = self.scrape_name(soup)

        self.driver.back()
        self.driver.back()
        sleep(0.5)

    def scrape_username(self, soup):
        try:
            return soup.find('h2', '_7UhW9').string
        except AttributeError:
            return 'None'

    def scrape_posts(self, soup):
        try:
            return soup.find('span', 'g47SY ').string
        except AttributeError:
            return '0'

    def scrape_subscribers(self, soup):
        try:
            return soup.find_all('span', 'g47SY ')[1].string
        except AttributeError:
            return '0'
        except IndexError:
            return '0'

    def scrape_following(self, soup):
        try:
            return soup.find_all('span', 'g47SY ')[2].string
        except AttributeError:
            return '0'
        except IndexError:
            return '0'

    def scrape_name(self, soup):
        try:
            return soup.find('h1', 'rhpdm').string
        except AttributeError:
            return ' '

    def scrape_profile_description(self, soup):
        try:
            div = soup.find('div', '-vDIg')
            return div.findChild('span').string
        except AttributeError:
            return ' '

    def scrape_profile_picture(self, soup):
        try:
            return soup.find('img', '_6q-tv')['src']
        except AttributeError:
            raise Exception('imgERROR')

    def you_subscrided(self, soup):
        try:
            if soup.find('button', '-fzfL'):
                return 'Yes'
        except AttributeError:
            return ' '

    def subscribed_on_you(self, soup):
        try:
            if soup.find('button', '_5f5mN').string == 'Follow Back':
                return 'Yes'
        except AttributeError:
            return ' '


def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

def main(hashtags, private_only: False, business_only: False, email_only: False, proxy_port: None, proxy_host: '', login, password):
    scraper = Cliker(hashtags, private_only, business_only,email_only, proxy_port, proxy_host)
    scraper.login(login, password)
    scraper.find_by_hashtag('follow')
    scraper.click_photos()


if __name__ == '__main__':
    main(['#follow', '#clown'], False, False, False, None, '', 'korolyofff', 'qwerty123LOL' )