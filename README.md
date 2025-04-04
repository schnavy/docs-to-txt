## Convert Web Docs to TXT

A small lightweight python script to scape an convert all content of a documentation website, including all subpages to a single txt file, which can be used to feed LLMs.

Usage:
```
pip install -r requirements.txt

python docstotxt.py <url> <links-selector> [<content-selector>]
```

- **url**: the base url of the docs, that includes a navigation element with all subpages
- **links-selector**: the element, from which the links should be scraped (use "body" for all links on the webpage)
- **content-selector (optional)**: the element which contains the information–prevents repeated scraping of unnecessary content

> [!NOTE] 
> This script will only scrape content on the same website based on its base url
