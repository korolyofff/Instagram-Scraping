'''Instagram WebScraping Followers Collector'''

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options

from scraper.models import Users
from time import sleep
import re


class Cliker:
    def __init__(self, profiles, private_only: False, business_only: False, email_only: False, proxy_port: None,
                 proxy_host: ''):
        self.business_only = business_only
        self.private_only = private_only
        self.email_only = email_only
        self.profiles = profiles

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

        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("intl.accept_languages", 'en-us')
        firefox_profile.update_preferences()

        self.options = Options()
        # self.options.headless = True
        self.options.profile = firefox_profile
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
        sleep(4)

    def find_profile(self, profile):
        self.driver.get('https://www.instagram.com/{}'.format(profile))
        sleep(2)

    def click_followers(self):
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()
        sleep(2)
        self.get_all_usernames(self.get_subscribers_count())

    def get_subscribers_count(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        scraper = Scraper(False, self.driver)

        try:
            followers = soup.find_all('span', 'g47SY')[1].text
            return float(str(scraper.get_followers(str(followers.replace(' ', '')))))

        except AttributeError:
            return '0'
        except IndexError:
            return '0'


    def get_all_usernames(self, subscribers):
        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            usernames_count = len(soup.find_all('a', 'FPmhX'))
            while usernames_count < subscribers - 10:
                element = self.driver.find_element_by_xpath('//div[@role="dialog"]//ul/parent::div')
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', element)
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                usernames_count = len(soup.find_all('a', 'FPmhX'))
                print('{} : {}'.format(usernames_count, subscribers))

            usernames_count = soup.find_all('a', 'FPmhX')
            for username in usernames_count:
                try:
                    self.driver.get('https://www.instagram.com/{}'.format(username.string))
                    scraper = Scraper(self.email_only, self.driver)
                    scraper.scrape_profile()
                except:
                    continue

        except AttributeError:
            print('89 FIX')

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
                following = self.get_following(str(self.scrape_following(soup)).replace(' ', ''))
                followers = self.get_followers(str(self.scrape_subscribers(soup)).replace(' ', ''))
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
            following = self.get_following(str(self.scrape_following(soup)).replace(' ', ''))
            followers = self.get_followers(str(self.scrape_subscribers(soup)).replace(' ', ''))
            full_name = self.scrape_name(soup)
            description = self.scrape_profile_description(soup)
            pic = self.scrape_profile_picture(soup)
            subscribed_on_your_profile = self.subscribed_on_you(soup)
            you_subscribed = self.you_subscrided(soup)
            user = Users(username=username, posts=posts, followers=followers, following=following, name=full_name,
                         description=description, email=' ', subscribed_on_your_profile=subscribed_on_your_profile,
                         you_subscribed=you_subscribed, picture=pic)
            user.save()

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

    def get_followers(self, followers):
        if 'm' in followers:
            return str(float(followers * 1000000))

        elif 'k' in followers:
            return str(float(followers * 1000))

        else: return followers

    def get_following(self, following):
        if 'm' in following:
            return str(float(following * 1000000))

        elif 'k' in following:
            return str(float(following * 1000))

        else: return following

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

def main(profiles, private_only: False, business_only: False, email_only: False, proxy_port: None, proxy_host: '', login, password):
    scraper = Cliker(profiles, private_only, business_only, email_only, proxy_port, proxy_host)
    scraper.login(login, password)
    for profile in profiles:
        profile = profile.replace(' ', '')
        scraper.find_profile(profile)
        scraper.click_followers()


if __name__ == '__main__':
    pass
