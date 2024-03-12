
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import Html2TextTransformer
from langchain.chains import create_extraction_chain
from crewai import Agent, Task
from langchain.tools import tool
import json
import re
import os
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.llms.ollama_functions import OllamaFunctions
import requests
from langchain.docstore.document import Document
from bs4 import BeautifulSoup 
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
search_tool = DuckDuckGoSearchRun()

def create_schema(property_names):
    """
    Create a JSON schema based on the list of property names provided.
    
    Args:
    - property_names (list): A list of strings representing property names.
    
    Returns:
    - schema (dict): A dictionary representing the JSON schema with the given properties.
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": property_names  # Assuming all properties are required
    }
    
    for name in property_names:
        # Assuming all properties are of type string. You can customize this part.
        schema["properties"][name] = {"type": "string"}
    
    return schema   


schema_input = input("Enter a list of properties that you want to extract, separated by commas: ")

# Split the input string into a list based on the comma delimiter
schema_list = [name.strip() for name in schema_input.split(',')]

# Print or use the schema as needed
schema = create_schema(schema_list)



class ScrapingTools:
    @tool("Scrape website content")    
    def scraping_tools(url: str):
        """This function helps in web scraping and extracting the data"""
        response = requests.get(url)
        html_content=response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        html_text = soup.get_text()
        doc = Document(page_content=html_text, metadata={})
        bs_transformer = Html2TextTransformer()
        docs_transformed = bs_transformer.transform_documents([doc], tags_to_extract=["span"])
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
        splits = splitter.split_documents(docs_transformed)
        return splits
        
class ExtractingTools:
    @tool("Extracting Data")    
    def extracting_tools(documents):
        """This function helps in extracting the data and saving"""
        print("In the extraction tool")
        system_prompt = (
                "You are an expert extraction algorithm. "
                "Only extract relevant and exact information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "you may omit the attribute's value."
            )
        
        llm = OllamaFunctions(model=os.getenv("MODEL_NAME"), temperature=0,system_prompt=system_prompt)
        def extract(content: str, schema: dict):
            print("h")
            return create_extraction_chain(schema=schema, llm=llm).invoke(content)
        scraped_data_raw=extract(schema=schema, content=documents)
        scraped_data=scraped_data_raw['text']
        print(scraped_data)
        return scraped_data
    

sraping_tool=ScrapingTools().scraping_tools
extractor_tool = ExtractingTools().extracting_tools


def main():
    url=input("Enter the URL of the Website\n")
    scraper = Agent(
            role='Web Scraper Agent',
            goal='Ask the user  URL, and scrape the website and then pass the data to the extraction agent so it can extract the data and save the data',
            backstory='You are expert in web scraping.',
            tools=[sraping_tool],
            llm=Ollama(model=os.getenv("MODEL_NAME"), temperature=0),
            allow_delegation=False,
            verbose=False,
        )
    extraction = Agent(
            role='Extraction',
            goal='Extract the given data and save this data',
            backstory='You are expert in extraction of the data.',
            llm= Ollama(model=os.getenv("MODEL_NAME"), temperature=0),
            tools=[extractor_tool],
            allow_delegation=True,
            verbose=False,
        )
    s_task= Task(
            description=f"""web scrape this url {url} then pass that data to the extraction agent""",
            agent=scraper
        )
    s2_task= Task(
            description=f"""Perform the extraction on the given data provided by scraper agent and save it""",
            agent=extraction)
 
    def get_base_url(url):
        try:
            # Parse the URL into components
            parsed_url = urlparse(url)
            # Split the path at the first slash and take the first part
            # which is the domain and TLD
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return base_url
        except Exception as e:
            print(f"An error occurred while parsing the URL: {e}")
            return None
    def get_next_link(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for 'a' tags containing 'Next' in their text
        next_link = soup.find('a', string=re.compile(r'(next|more|next page|load more)', re.IGNORECASE))
     
        # If 'Next' link is not found, look for other common pagination classes
        if next_link is None:
            next_link = soup.find('a', class_=re.compile(r'(next|more|load more|next page)', re.IGNORECASE)) 
            
        # If 'Next' link is still not found, handle other pagination methods as needed
        if next_link is None:
            next_link = soup.find('a', {'title': 'Next'})
        if next_link is None:
            next_link = soup.find('li', {'class':'next'})
         
        if next_link is not None:
            next_url = next_link.get('href')
            if next_url is None:
                next_url=next_link.find('a')['href']
                print("next url",next_url)
            if next_url.startswith('/'):
                base_url = get_base_url(url)
                next_url = base_url + next_url
            return next_url

        # If no next link is found
        return None


    while url is not None:
        print("Scrapping of Page",url)
        print("Running scraping task...")
        scraped_data = s_task.agent.tools[0](url)  # Assuming there's only one tool for scraping
        print("Scraping done.")
        extracted_data=[]
        # Step0 2: Run the extraction task
        print("Running extraction task...")
        for split in scraped_data:
            extracted_data.append(s2_task.agent.tools[0](split.page_content))
             
        # Assuming there's only one tool for extraction
        print("Extraction done.")
        json_data = json.dumps(extracted_data)
        with open(os.getenv("FILE_NAME")+".json", 'a') as file:
            file.write(json_data)
        

        print("Scraped data has been written to the file.")
        check=os.getenv("PAGINATION")
        if check.lower() == "true":
            url = get_next_link(url)
        else:
            url = None
            print(url)

        
    
    
# Run the main function
if __name__ == "__main__":
    main()
