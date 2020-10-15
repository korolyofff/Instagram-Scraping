'''Instagram WebScraping'''

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep


# TODO SCRAPING PROFILES
# TODO SELENIUM WAIT
# TODO EXCEPT ATTR ERROR
# TODO CHANGE SEARCHING BY HASHTAG (by URL)
class Cliker:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--lang=en')
        self.options.add_argument('--start-maximized')
        try:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)

        except InvalidArgumentException:

            print('Close Chrome and try again')

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
        # searcher = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')
        # searcher.send_keys(hashtag)
        # sleep(3)
        # html = self.driver.page_source
        # soup = BeautifulSoup(html, 'lxml')
        # tags = soup.find_all('span', 'Ap253')
        # for tag in tags:
        #     try:
        #         if tag.string == hashtag:
        #             element = tag.findParent('a', 'yCE8d')
        #             xpath_element = xpath_soup(element)
        #             hashtag_button = self.driver.find_element_by_xpath(xpath_element)
        #             hashtag_button.click()
        #             break
        #
        #     except AttributeError:
        #         continue

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
        scraper = Scraper()
        scraper.scrape_profile()


class Scraper(Cliker):

    def scrape_profile(self):
        sleep(1)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
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

def main():
    scraper = Cliker()
    scraper.login('korolyofff', 'qwerty123LOL')
    scraper.find_by_hashtag('#follow')
    scraper.click_photos()

if __name__ == '__main__':
    main()

