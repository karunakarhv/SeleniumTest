import unittest
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Constructing Web Page
class WebPage(object):
    def __init__(self, title, xpath, element, value):
        self.title = title
        self.xpath = xpath
        self.element = element
        self.value = value

# Racing Page
class RacingPage(unittest.TestCase):

    racingUrl = 'https://www.unibet.com.au/racing'
    raceType = {'race.T':'Thoroughbred', 'race.G': 'Greyhound', 'race.H':'Harness'}

    betslip = {
        'eventName': WebPage(
            title = ['Event Name'],
            xpath = '//*/div[@data-test-id="bet-card-race-title"]',
            element = None,
            value = []
        ),
        'eventTypeIcon': WebPage(
            title = ['Event Type'],
            xpath = '//*/div[@class="sc-bCwfaz hzzSzX"]/*[name()="svg"]',
            element = None,
            value = []
        ),
        'runner': WebPage(
            title = ['Runner Sequence', 'Runner Name'],
            xpath = '//*/div[@data-test-id="bet-history-runner"]',
            element = None,
            value = []
        ),
        'betOddsPrice': WebPage(
            title = ['Price'],
            xpath = '//*/span[@data-test-id="bet-card-bet-odds-price-per-market"]',
            element = None,
            value = []
        ),
        'betOddsPriceType': WebPage(
            title = ['Market'],
            xpath = '//*/span[@data-test-id="bet-card-bet-odds-price-type"]',
            element = None,
            value = []
        )
    }

    def setUp(self):
        # create a new Firefox session
        self.webDriver = webdriver.Firefox()
        if self.webDriver is not None:
            try:
                self.webDriver.implicitly_wait(10)
                self.webDriver.maximize_window()
                # navigate to the application home page
                self.webDriver.get(RacingPage.racingUrl)
                self.assertEqual('Horse Racing Betting & Odds | Racing Results Today | Unibet Australia',
                            self.webDriver.title)
            except Exception:
                print('Unable to load Home Page')
                return

    def verifyBetSlip(self):
        try:
            # Clicking on Item sorting with lowest price to highest price
            fixedWinButton = self.webDriver.find_element_by_xpath('//*/button[@class="sc-fvNhHS jcWxmD  "]')
            fixedWinButton.click()
        except NoSuchElementException:
            self.webDriver.save_screenshot('Error-verifyBetSlip')
            return False

        # Populating Element Xpath
        if not self.populateElementXpath():
            print('Cannot populate Element xpath')
            return False

        # Populating Element Text Value
        if not self.populateElementText():
            print('Cannot populate Element text')
            return False

        # Verifying the betslip values printed and the screenshot taken.
        if not self.displayBetSlip():
            return False

        self.webDriver.save_screenshot('BetSlipPage.png')

        return True

    def populateElementXpath(self):
        try:
            for items in RacingPage.betslip:
                pageObject = RacingPage.betslip[items]
                pageObject.element = self.webDriver.find_element_by_xpath(pageObject.xpath)
        except NoSuchElementException:
            self.webDriver.save_screenshot('Error-populateElementXpath')
            return False
        return True

    def populateElementText(self):
        try:
            for items in RacingPage.betslip:
                pageObject = RacingPage.betslip[items]
                if items == 'eventTypeIcon':
                    pageObject.value.append(pageObject.element.get_attribute('variant'))
                elif items == 'runner':
                    valueList = pageObject.element.text.split('.')
                    pageObject.value.append(valueList[0])
                    pageObject.value.append(valueList[1])
                else:
                    pageObject.value.append(pageObject.element.text)
        except AttributeError:
            self.webDriver.save_screenshot('Error-populateElementText')
            return False
        return True

    def displayBetSlip(self):
        for items in RacingPage.betslip:
            pageObject = RacingPage.betslip[items]
            if items == 'eventTypeIcon':
                if pageObject.value[0] in RacingPage.raceType:
                    print('{} {}'.format(pageObject.title[0],
                                                RacingPage.raceType[pageObject.value[0]]))
            elif items == 'runner':
                print('{} {}'.format(pageObject.title[0], pageObject.value[0]))
                print('{} {}'.format(pageObject.title[1], pageObject.value[1]))
            else:
                print('{} {}'.format(pageObject.title[0], pageObject.value[0]))
        return True

    def clickOnLowestFixedPrice(self):
        winOrPlaceList = []
        try:
            buttonList = self.webDriver.find_elements_by_xpath('//*/button[@data-test-id="event-card-sortby-Price"]')
            for button in buttonList:
                if button.text == 'FIXED':
                    winOrPlaceList.append(button)
            winOrPlaceList[0].click()
        except NoSuchElementException:
            self.webDriver.save_screenshot('Error-clickOnLowestFixedPrice')
            return False
        return True

    def goToLastElementInNextToGo(self, anchorElements):
        try:
            # Last element which has 'F' Prices Icon
            test = anchorElements[-1].find_elements_by_xpath('//button/span[1]/div[1]/*[name()="svg"][@data-test-id="ntg-seq-pricef"]')
            if test:
                # Clicking on 'F' Prices Icon
                actionChains = ActionChains(self.webDriver)
                actionChains.move_to_element(test[-1]).click().perform()
                time.sleep(5)
                self.webDriver.save_screenshot('NavigateToRacingPage.png')
        except NoSuchElementException:
            print('No Element found')
            return False
        return True

    def test_bet_slip(self):
        anchorElements = []
        try:
            # Listing the next to go event list
            containers = self.webDriver.find_elements_by_xpath('//div[@data-test-id="ntg-event-list"]')
            for items in containers:
                # Finding all the anchor elements and populating into list
                for td in items.find_elements_by_tag_name('a'):
                    anchorElements.append(td)
        except NoSuchElementException:
            self.webDriver.save_screenshot('Error-test_bet_slip')
            return False

        # Click on the last event in the Next To Go that has the “F” (has prices) icon
        if not self.goToLastElementInNextToGo(anchorElements):
            print('Step 2 - Cannot click Last Event in the NTG failed')
            return False
        # Navigate to the event and click on lowest FIXED price
        if not self.clickOnLowestFixedPrice():
            print('Step 3 - Cannot click on Lowest Fixed Price')
            return False
        # Verify the following is populated to the betslip
        if not self.verifyBetSlip():
            print('Step 4 - Cannot display bet slip')
            return False

        return True

    def tearDown(self):
        # close the browser window
        self.webDriver.quit()

if __name__ == '__main__':
    unittest.main()