'''Instagram WebScraping Hashtag Collector'''

from bs4 import BeautifulSoup
from django.db import DataError
from seleniumwire import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, TimeoutException, \
    ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
                    'http': 'http://{}'.format(proxy),
                    'https': 'https://{}'.format(proxy),
                    'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
                }
            }

        fireFoxOptions = webdriver.FirefoxOptions()
        # fireFoxOptions.headless = True
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("intl.accept_languages", 'en-us')
        firefox_profile.update_preferences()

        try:
            self.driver = webdriver.Firefox(seleniumwire_options=self.options, firefox_profile=firefox_profile,
                                            firefox_options=fireFoxOptions)
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(1024, 768)

        except InvalidArgumentException:
            raise exit()

        self.driver.get('https://www.instagram.com/')

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

    def find_by_hashtag(self, hashtag):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')))
        except:
            pass

        self.driver.get('https://www.instagram.com/explore/tags/{}/'.format(hashtag))
        sleep(2)

    def scroll_quantity(self, soup):
        try:
            quantity = soup.find('span', 'g47SY').string
            quantity = quantity.replace(',', '')
            quantity = quantity.replace(' ', '')

            return int(quantity) // 12

        except AttributeError:
            return 300

    def click_photos(self):
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[3]')))

        coord = 2000
        self.driver.execute_script("window.scrollTo(0, {})".format(coord))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        lines = soup.find_all('div', 'Nnq7C')
        for line in lines:
            photos = line.findChildren('div', '_9AhH0')
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
                try:
                    self.driver.find_element_by_class_name('aOOlW').click()
                    sleep(3)
                except:
                    pass
                try:
                    photo.click()
                except:
                    with open('html.txt','w') as f:
                        f.write(str(self.driver.page_source))
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
                    photos = line.findChildren('div', '_9AhH0')
                    for photo in photos:
                        try:
                            photo = self.driver.find_element_by_xpath(xpath_soup(photo))
                        except AttributeError:
                            sleep(2)
                            photo = self.driver.find_element_by_xpath(xpath_soup(photo))
                        except NoSuchElementException:
                            continue
                        try:
                            try:
                                self.driver.find_element_by_class_name('aOOlW').click()
                                sleep(3)
                            except:
                                pass

                            photo.click()
                            self.click_profile()

                        except ElementClickInterceptedException:
                            continue

    def click_profile(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.e1e1d > span:nth-child(1) > a:nth-child(1)')))
        except TimeoutException:
            pass
        except NoSuchElementException:
            self.driver.back()
            return

        try:
            self.driver.find_element_by_css_selector('.e1e1d > span:nth-child(1) > a:nth-child(1)').click()
        except NoSuchElementException:
            self.driver.back()
            return

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[1]/span')))
        except TimeoutException:
            pass

        scraper = Scraper(self.email_only, self.driver)
        scraper.scrape_profile()


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
                following = str(self.scrape_following(soup)).replace(' ', '')
                followers = str(self.scrape_subscribers(soup)).replace(' ', '')
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
                try:
                    user.save()
                except:
                    pass
        else:
            username = self.scrape_username(soup)
            posts = str(self.scrape_posts(soup)).replace(' ', '')
            following = str(self.scrape_following(soup)).replace(' ', '')
            followers = str(self.scrape_subscribers(soup)).replace(' ', '')
            full_name = self.scrape_name(soup)
            description = self.scrape_profile_description(soup)
            email = self.scrape_email(soup)
            pic = self.scrape_profile_picture(soup)
            subscribed_on_your_profile = self.subscribed_on_you(soup)
            you_subscribed = self.you_subscrided(soup)
            user = Users(username=username, posts=posts, followers=followers, following=following, name=full_name,
                         description=description, email=email, subscribed_on_your_profile=subscribed_on_your_profile,
                         you_subscribed=you_subscribed, picture=pic)
            try:
                user.save()
            except:
                pass

        self.driver.back()
        self.driver.back()
        sleep(1)

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


def main(hashtags, private_only: False, business_only: False, email_only: False, proxy_port: None, proxy_host: '',
         login, password):
    scraper = Cliker(hashtags, private_only, business_only, email_only, proxy_port, proxy_host)
    scraper.login(login, password)
    for hashtag in hashtags:
        hashtag = hashtag.replace(' ', '')
        scraper.find_by_hashtag(hashtag)
        scraper.click_photos()


if __name__ == '__main__':
    pass
