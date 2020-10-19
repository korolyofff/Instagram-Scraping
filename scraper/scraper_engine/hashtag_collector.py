'''Instagram WebScraping Hashtag Collector'''

from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options
from scraper.models import Users
from time import sleep
import re


class Cliker:
    def __init__(self, hashtags, private_only: False, business_only: False, email_only: False, proxy_port: None,
            proxy):
        self.business_only = business_only
        self.private_only = private_only
        self.email_only = email_only
        self.hashtags = hashtags
        self.options = None
        if proxy != '':
            self.options = {
                'proxy': {
                    'https': proxy,
                    'http': proxy,
                    'no_proxy': 'localhost,127.0.0.1,dev_server:8889'
                }
            }
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("intl.accept_languages", 'en-us')
        firefox_profile.update_preferences()

        try:
            self.driver = webdriver.Firefox(seleniumwire_options=self.options, firefox_profile=firefox_profile)
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
            quantity = quantity.replace(' ', '')

            return int(quantity) // 12

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
            for photo in photos:
                try:
                    if xpath_soup(photo) == '/html/body/div[1]/section/main/article/div[2]/div/div[15]/div[1]':
                        continue

                    if xpath_soup(photo) == '/html/body/div[1]/section/main/article/div[2]/div/div[14]/div[1]':
                        continue
                    try:
                        photo = self.driver.find_element_by_xpath(xpath_soup(photo))

                    except NoSuchElementException:
                        continue

                except AttributeError:
                    sleep(2)
                    if xpath_soup(photo) == '/html/body/div[1]/section/main/article/div[2]/div/div[15]/div[1]':
                        continue

                    if xpath_soup(photo) == '/html/body/div[1]/section/main/article/div[2]/div/div[14]/div[1]':
                        continue

                    try:
                        photo = self.driver.find_element_by_xpath(xpath_soup(photo))
                    except NoSuchElementException:
                        continue

                photo.click()
                self.click_profile()

        if self.scroll_quantity(soup) > 40 // 12:
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
                        try:
                            photo = self.driver.find_element_by_xpath(xpath_soup(photo))
                        except AttributeError:
                            sleep(2)
                            photo = self.driver.find_element_by_xpath(xpath_soup(photo))
                        except NoSuchElementException:
                            continue

                        photo.click()
                        self.click_profile()

    def click_profile(self):
        sleep(1.5)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        try:
            profile_xpath = xpath_soup(soup.find('a', 'yWX7d'))
        except AttributeError:
            sleep(2)
            profile_xpath = xpath_soup(soup.find('a', 'yWX7d'))

        self.driver.find_element_by_xpath(profile_xpath).click()
        sleep(1)
        scraper = Scraper(self.email_only, self.driver)
        scraper.scrape_profile()

class Scraper():
    def __init__(self, email_only, driver):
        self.email_only = email_only
        self.driver = driver

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
        sleep(3)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        if self.email_only:
            if self.has_email(soup):
                username = self.scrape_username(soup)
                posts = str(self.scrape_posts(soup)).replace(' ', '')
                following = str(self.scrape_following(soup)).replace(' ', '')
                followers = str(self.scrape_subscribers(soup)).replace(' ', '')
                full_name = self.scrape_name(soup)
                description = self.scrape_profile_description(soup)
                email = ''
                pic = self.scrape_profile_picture(soup)
                subscribed_on_your_profile = self.subscribed_on_you(soup)
                you_subscribed = self.you_subscrided(soup)
                user = Users(username=username, posts=posts, followers=followers, following=following, name=full_name,
                             description=description, email=email, subscribed_on_your_profile=subscribed_on_your_profile,
                             you_subscribed=you_subscribed, picture=pic)
                user.save()
        else:
            username = self.scrape_username(soup)
            posts = str(self.scrape_posts(soup)).replace(' ', '')
            following = str(self.scrape_following(soup)).replace(' ', '')
            followers = str(self.scrape_subscribers(soup)).replace(' ', '')
            full_name = self.scrape_name(soup)
            description = self.scrape_profile_description(soup)
            pic = self.scrape_profile_picture(soup)
            subscribed_on_your_profile = self.subscribed_on_you(soup)
            you_subscribed = self.you_subscrided(soup)
            user = Users(username=username, posts=posts, followers=followers, following=following, name=full_name,
                         description=description, email=' ', subscribed_on_your_profile=subscribed_on_your_profile,
                         you_subscribed=you_subscribed, picture=pic)
            user.save()

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
            return soup.find_all('span', 'g47SY')[0].string
        except AttributeError:
            return '0'
        except IndexError:
            return '0'

    def scrape_subscribers(self, soup):
        try:
            return soup.find_all('span', 'g47SY')[1].text
        except AttributeError:
            return '0'
        except IndexError:
            return '0'

    def scrape_following(self, soup):
        try:
            return soup.find_all('span', 'g47SY')[2].text
        except AttributeError:
            return '0'
        except IndexError:
            return '0'

    def scrape_name(self, soup):
        try:
            return soup.find('h1', 'rhpdm').text
        except AttributeError:
            return ' '

    def scrape_profile_description(self, soup):
        try:
            div = soup.find('div', '-vDIg')
            return div.findChild('span').text
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
            else:
                return ' '
        except AttributeError:
            return ' '

    def subscribed_on_you(self, soup):
        try:
            if soup.find('button', '_5f5mN').string == 'Follow Back':
                return 'Yes'
            else:
                return ' '
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
    for hashtag in hashtags:
        hashtag = hashtag.replace(' ', '')
        scraper.find_by_hashtag(hashtag)
        scraper.click_photos()


if __name__ == '__main__':
    pass