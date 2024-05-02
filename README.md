# MPEPjson
RDMS MPEP to JSON MPEP

download latest chromedriver
https://chromedriver.chromium.org/

optionally read Chrome for Testing (CfT)
https://developer.chrome.com/blog/chrome-for-testing

find CfT version that will work with your version chromedriver
https://github.com/GoogleChromeLabs/chrome-for-testing#json-api-endpoints

run rdms_selenium_scraper.ipynb

run html_to_json_bs4parser.ipynb
this creates a giant single json file
and cleans it

set up ollama on local machine
choose a LLM (e.g. phi3) and run 'ollama run phi3' from command line

while ollama local service is running on localhost:
run llama_indexer.ipynb

test the embedded MPEP by asking it questions in the final cell!
