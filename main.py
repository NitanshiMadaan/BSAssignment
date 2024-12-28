# Web Scraping with Selenium
git --versionimport os
import time

import requests
from browserstack.local import Local
from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Initialize the translator
translator = Translator()

# Access BrowserStack credentials from environment variables
browserstack_username = os.getenv('BROWSERSTACK_USERNAME')
browserstack_access_key = os.getenv('BROWSERSTACK_ACCESS_KEY')

if not browserstack_username or not browserstack_access_key:
    raise ValueError("BrowserStack credentials not set in environment variables.")

# Start the BrowserStack Local binary (if you need to test locally hosted sites)
bs_local = Local()
bs_local_args = {"key": browserstack_access_key}
bs_local.start(**bs_local_args)

# Set up capabilities using the new method in Selenium 4
options = Options()
options.set_capability('browser', 'Chrome')
options.set_capability('browser_version', 'latest')
options.set_capability('os', 'Windows')
options.set_capability('os_version', '11')
options.set_capability('name', 'Opinion Articles Scraper')  # Test name
options.set_capability('build', 'build_1')
options.set_capability('browserstack.local', 'false')
options.set_capability('browserstack.debug', 'true')  # Optional: Enable debugging

# Setup WebDriver for BrowserStack using ClientConfig

# Create a remote connection object and pass the BrowserStack credentials securely
driver = webdriver.Remote(
    command_executor=f'https://{browserstack_username}:{browserstack_access_key}@hub-cloud.browserstack.com/wd/hub',
    options=options
)


def get_opinion_articles():
    # Open El País website
    driver.get('https://elpais.com/opinion/')
    time.sleep(5)  # Allow page to load

    # Get the first 5 article elements
    articles = driver.find_elements(By.CSS_SELECTOR, '.articulo')[:5]

    article_data = []

    for article in articles:
        # Extract title and content
        title = article.find_element(By.CSS_SELECTOR, '.articulo-titulo').text
        content = article.find_element(By.CSS_SELECTOR, '.articulo-contenido').text

        # Extract the cover image (if available)
        try:
            img_url = article.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
            img_data = requests.get(img_url).content
            with open(f'./images/{title[:10]}.jpg', 'wb') as f:
                f.write(img_data)
        except Exception as e:
            print("No image found:", e)

        article_data.append({'title': title, 'content': content})

    return article_data


# Get the articles
articles = get_opinion_articles()

# Print the titles and content in Spanish
for article in articles:
    print(f"Title (Spanish): {article['title']}")
    print(f"Content: {article['content']}\n")

# Stop the BrowserStack Local instance after the test is done
bs_local.stop()

# Translate article titles to English
def translate_titles(articles):
    translated_titles = []

    for article in articles:
        translated_title = translator.translate(article['title'], src='es', dest='en').text
        translated_titles.append({'original': article['title'], 'translated': translated_title})

    return translated_titles


# Translate the titles
translated_titles = translate_titles(articles)

# Print the translated titles
for item in translated_titles:
    print(f"Original Title (Spanish): {item['original']}")
    print(f"Translated Title (English): {item['translated']}\n")

# Analyze Translated Headers for Repeated Words

from collections import Counter
import re


def analyze_repeated_words(titles):
    # Join all translated titles into one string
    all_titles = ' '.join([title['translated'] for title in titles])

    # Remove punctuation and split into words
    words = re.findall(r'\w+', all_titles.lower())

    # Count word occurrences
    word_counts = Counter(words)

    # Filter out words that appear more than twice
    repeated_words = {word: count for word, count in word_counts.items() if count > 2}

    return repeated_words


# Analyze the repeated words
repeated_words = analyze_repeated_words(translated_titles)

# Print repeated words and their counts
print("Repeated words (appeared more than twice):")
for word, count in repeated_words.items():
    print(f"{word}: {count}")

# Cross Browser Testing with Browserstack

desired_caps = {
    'browserstack.local': 'false',
    'browser': 'Chrome',
    'browser_version': 'latest',
    'os': 'Windows',
    'os_version': '10',
    'name': 'Opinion Articles Scraper',
    'build': 'build_1',
}

# Connect to BrowserStack with desired capabilities for different browsers and OS
for browser in ['Chrome', 'Firefox', 'Safari', 'Edge']:
    for os_version in ['Windows 10', 'macOS Monterey']:
        desired_caps['browser'] = browser
        desired_caps['os_version'] = os_version
        driver = webdriver.Remote(
            command_executor=f'https://{browserstack_username}:{browserstack_access_key}@hub-cloud.browserstack.com/wd/hub',
            options=options
        )

        # Run your scraping code here on BrowserStack
        # For simplicity, assuming get_opinion_articles() and other methods are already defined
        articles = get_opinion_articles()
        translated_titles = translate_titles(articles)
        repeated_words = analyze_repeated_words(translated_titles)
        print(repeated_words)

        driver.quit()
