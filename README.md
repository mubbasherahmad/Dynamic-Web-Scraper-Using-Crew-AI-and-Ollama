# Dynamic Web Scraper Using Crew AI and Ollama

## Introduction

This application serves as a dynamic web scraper designed to efficiently extract data from websites using Crew ai and Ollama Locally Hosted Models. It leverages the capabilities of the Ollama model, which is an alternative to OpenAI's GPT-4. The choice to use Ollama over GPT-4 is primarily due to cost-effectiveness, as Ollama provides a more affordable solution while still delivering powerful natural language processing and understanding capabilities. The application is built with flexibility in mind, allowing users to specify the type of data they wish to extract, and it is equipped to handle pagination for comprehensive data collection.

## Tools

This web scraper is built using a combination of Python libraries and frameworks, each contributing to different aspects of the application:

- **LangChain**: Provide tools for integrating large language models (LLMs) like Ollama into applications, as well as utilities for text splitting and HTML-to-text transformations.
- **CrewAI**: Facilitates the creation of agents and tasks, enabling a structured approach to web scraping and data extraction.
- **Requests**: A popular HTTP library for Python, used to send HTTP requests and interact with web pages.
- **BeautifulSoup**: A Python library for parsing HTML and XML documents, used for web scraping and extracting data from web pages.
- **Dotenv**: A Python library that allows the application to load environment variables from a `.env` file, keeping sensitive information like API keys secure.
- **Urllib**: A Python module used for URL handling, helping to parse and construct URLs.
- **JSON**: A lightweight data interchange format, used for storing and exchanging the extracted data.
- **Re**: The Python module for working with regular expressions, which helps in identifying patterns in text, such as pagination links.

## How It Works

The application operates in several stages:

1. **User Input**: The user is prompted to enter a list of properties they wish to extract from the target website, which is then used to create a JSON schema.
2. **Web Scraping**: The application asks the user for the URL of the website they want to scrape. It then uses the BeautifulSoup library to navigate the HTML content and extract the text.
3. **Data Extraction**: The extracted text is passed to an extraction agent powered by the Ollama model, which processes the text and extracts the relevant data based on the provided schema.
4. **Pagination Handling**: If pagination is enabled, the application will automatically find the 'Next' link on the page and continue scraping subsequent pages until no further pages are found.
5. **Data Storage**: The extracted data is saved in a JSON file for later use or analysis.

## Example/Demo

Here's a brief demonstration of how the application works:

1. The user inputs the properties they want to extract, such as "type_of_property_listed, location_of_property_listed, size_of_property_listed,price_of_property_listed, purpose_of_property_listed".
2. They then provide the URL of the OLX or Zameen listing page they wish to scrape such as "https://www.zameen.com/Homes/Islamabad-3-1.html".
3. The web scraper agent begins its task, scraping the website content and passing the data to the extraction agent.
4. The extraction agent processes the content, extracting information matching the user-defined schema.
5. The extracted data is appended to a JSON file named `zameen_scraped_data.json`.

## How to Start

To run the application, follow these steps:

1. Ensure you have Python installed on your system.
2. Clone the repository to your local machine.
3. Install the required dependencies by running `pip install -r requirements.txt`.
4. Create a `.env` file in the root directory and define the `MODEL_NAME` and `PAGINATION` and `FILE_NAME` environment variables.
5. Run the application by executing `python scraper.py` in your terminal.
6. Follow the on-screen prompts to input the properties and URL for scraping.

Before running the application, make sure you have read and understood the terms of service of the website you intend to scrape, as web scraping may not be allowed on some websites without permission.
