'''Instagram WebScraping Following Collector'''

from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.models import Users
from time import sleep
import re


class Cliker:
    def __init__(self, profiles, private_only: False, business_only: False, email_only: False, proxy_port: None,
                 proxy: ''):
        self.business_only = business_only
        self.private_only = private_only
        self.email_only = email_only
        self.profiles = profiles
        self.options = None

        if proxy != '':
            self.options = {
                'proxy': {
                    'http': 'http://{}'.format(proxy),
                    'https': 'https://{}'.format(proxy),
                    'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
                }
            }

        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("intl.accept_languages", 'en-us')
        firefox_profile.update_preferences()

        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True

        try:
            self.driver = webdriver.Firefox(seleniumwire_options=self.options, firefox_profile=firefox_profile,
                                            firefox_options=fireFoxOptions)
            sleep(5)
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(1024, 768)

        except InvalidArgumentException:
            print('Close Firefox and try again')

        self.driver.get('https://www.instagram.com/')
        sleep(2)

    def login(self, phone, password):
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')))
        except TimeoutException:
            raise TimeoutException

        phone_field = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
        password_field = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
        phone_field.send_keys(phone)
        password_field.send_keys(password)
        login = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div')
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="loginForm"]/div/div[3]/button/div')))
        self.driver.execute_script("arguments[0].click();", login)

    def find_profile(self, profile):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')))
        except: pass

        self.driver.get('https://www.instagram.com/{}'.format(profile))
        sleep(2)

    def click_following(self):
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')))
        except TimeoutException:
            raise TimeoutException

        try:
            element = self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a')
            self.driver.execute_script("arguments[0].click();", element)

        except:
            raise AttributeError

        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//ul/parent::div')))
        except TimeoutException:
            raise TimeoutException

        self.get_all_usernames(self.get_subscribers_count())

    def get_subscribers_count(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        scraper = Scraper(False, self.driver)

        try:
            followers = soup.find_all('span', 'g47SY')[1].text
            followers = followers.replace(' ', '')
            if 'm' in followers:
                followers = followers.replace('m', '')
                followers = int(followers) * 1000000
            if 'k' in followers:
                followers = followers.replace('k', '')
                followers = int(followers) * 1000

            return float(str(scraper.get_followers(str(followers))))

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

            usernames_count = soup.find_all('a', 'FPmhX')
            for username in usernames_count:
                self.driver.get('https://www.instagram.com/{}/'.format(username.string))
                try:
                    WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[1]/span')))
                except TimeoutException:
                    raise TimeoutException

                scraper = Scraper(self.email_only, self.driver)
                scraper.scrape_profile()


        except AttributeError:
            pass


class Scraper():
    def __init__(self, email_only, driver):
        self.email_only = email_only
        self.driver = driver

    def has_email(self, soup):
        try:
            div = soup.find('div', '-vDIg')
            description = div.findChild('span').text
            email = re.findall(r'(\w+@.+\.\w+)', description)
            if len(email) > 0:
                return True
            else:
                return False

        except AttributeError:
            return False

    def scrape_email(self, soup):
        try:
            div = soup.find('div', '-vDIg')
            description = div.findChild('span').text
            result = re.findall(r'(\w+@.+\.\w+)', description)[0]
            return result
        except AttributeError:
            return ' '
        except IndexError:
            return ' '

    def scrape_profile(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        if self.email_only:
            if self.has_email(soup):
                username = self.scrape_username(soup)
                posts = str(self.scrape_posts(soup)).replace(' ', '')
                following = self.scrape_following(soup)
                followers = self.scrape_subscribers(soup)
                full_name = self.scrape_name(soup)
                description = self.scrape_profile_description(soup)
                email = self.scrape_email(soup)
                pic = self.scrape_profile_picture(soup)
                subscribed_on_your_profile = self.subscribed_on_you(soup)
                you_subscribed = self.you_subscrided(soup)
                user = Users(username=username, posts=posts, followers=followers, following=following, name=full_name,
                             description=description, email=email,
                             subscribed_on_your_profile=subscribed_on_your_profile,
                             you_subscribed=you_subscribed, picture=pic)
                user.save()
        else:
            username = self.scrape_username(soup)
            posts = str(self.scrape_posts(soup)).replace(' ', '')
            following = self.scrape_following(soup)
            followers = self.scrape_subscribers(soup)
            full_name = self.scrape_name(soup)
            description = self.scrape_profile_description(soup)
            email = self.scrape_email(soup)
            pic = self.scrape_profile_picture(soup)
            subscribed_on_your_profile = self.subscribed_on_you(soup)
            you_subscribed = self.you_subscrided(soup)
            user = Users(username=username, posts=posts, followers=followers, following=following, name=full_name,
                         description=description, email=email, subscribed_on_your_profile=subscribed_on_your_profile,
                         you_subscribed=you_subscribed, picture=pic)
            user.save()
        sleep(0.5)

    def scrape_username(self, soup):
        try:
            return soup.find('h2', '_7UhW9').string
        except AttributeError:
            try:
                sleep(1)
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
            pic = soup.find('img', '_6q-tv')['src']
            if len(pic) < 250:
                return pic
            else:
                return ' '

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
            followers = followers.replace('m', '').replace(' ', '')
            return str(int(followers * 1000000))

        elif 'k' in followers:
            followers = followers.replace('k', '').replace(' ', '')
            return str(int(followers * 1000))

        else:
            return followers

    def get_following(self, following):
        if 'm' in following:
            following = following.replace('k', '').replace(' ', '')

            return str(int(following * 1000000))

        elif 'k' in following:
            following = following.replace('k', '').replace(' ', '')

            return str(int(following * 1000))

        else:
            return following


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


def main(profiles, private_only: False, business_only: False, email_only: False, proxy_port: None, proxy_host: '',
         login, password):
    scraper = Cliker(profiles, private_only, business_only, email_only, proxy_port, proxy_host)
    scraper.login(login, password)
    for profile in profiles:
        profile = profile.replace(' ', '')
        scraper.find_profile(profile)
        scraper.click_following()


if __name__ == '__main__':
    pass
