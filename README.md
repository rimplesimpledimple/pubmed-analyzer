
# Pubmed Paper Analyzer
A tool to get pubmed papers and summarize them - get summary, tables, etc.

# Approach

## Analysis
- Downloaded and analysed the papers listed in assignment to get a rough idea about the size and page count for average paper.
    - Successfully downloaded: 199(294 total)
    - Size distribution:
        - Largest: 34 MB (https://pubmed.ncbi.nlm.nih.gov/38798673/), 93 Pages 😱
        - Average: 5.6 MB
        - The size is mostly large due to inlcusion of images/figures/charts.
    - Page Count distribution:
        - [!Page Count](./page_distribution.png)
        - Max: 93 (https://pubmed.ncbi.nlm.nih.gov/38798673/)
        - Median:16 
        - Over all papers, avg. number characters per page including spaces: ~4450    

## Requirements for our app
- Support upto 100 page research paper  - this should cover most of the papers 
- How many parallel requests do we need to support?
    - we would be bounded by the memory so the goal is to maximize the number of parallel requests for a given memory.
    - assuming rate limits are high enough for both the LLMs and the pubmed api(3 per second without api). 

- Minimising cost:
    - keep the number of tokens to a minimum.


## Assumptions
- LLMs have a context window of 128k tokens. True for gpt, claude, gemini, etc.
    - assuming(as analysis showed) 4450 characters per page ~= 1000 tokens per page.
    - so, 128k tokens / 1000 tokens ~= 128 pages.
- Rate limits are high enough for both the LLMs and the pubmed api
    - *current pubmed api allows 3 requests per second* - going to assume that this would be enough for our use case.

## Analysis algorithms
- Directly send the entire paper to the LLM as pdf
    -  Some LLMs support pdf input, claude(max 100 pages, 32MB)(https://docs.anthropic.com/en/docs/build-with-claude/pdf-support)  
    -  Cons:
        - More tokens to be processed, image based cost(2x).
        - Could be slow as we need to send the entire pdf which could be large.
    -  Pros:
        - simple to implement, no more pdf parsing.

- Send the entire txt content of the pdf to the LLM
    - Parse the pdf using a library(pymupdf) and send the entire txt content to the LLM.
    -  Pros:
        - less tokens compared to pdf.
    -  Cons:
        - parsing pdf would lose the layout, could be less accurate for tables.

- Hybrid approach
    - Send the entire txt content of the pdf to the LLM with Page Numbers.
    - Ask the LLM about the specific page number with the main table.
    - Pass the image of the table to the LLM.


# Design
![Design](./design.png)

## Downloader
- works only for papers with pmcid(pubmed central id). 
- rate limited to 3 requests per second by pubmed api.

## Analyzer
- PdfDumpAnalyzer
    - send the entire pdf to the LLM.
- TextDumpAnalyzer
    - parse the pdf using a library(pymupdf) and send the entire txt content to the LLM.
- HybridAnalyzer[to be added] 

# Logging and Error Handling
- Global logger, logging at the source where the error occurs.
- Error handling: same, raised at source. One global exception handler to log the error and reraise it.

# Setup instructions
- clone the repo
- python version <3.11 (biopython dependency supports only upto 3.11)(using mac? `brew install python@3.11`)
- create a virtual environment and install the dependencies using `pip install -r requirements.txt`
- setup the environment variables, .env in root directory. Add "CLAUDE_API_KEY"

# Usage
## Streamlit UI
- run frontend `python streamlit run app.py`
- backend server `python main.py`

## Parallel processing from terminal


## Using API
- Endpoints, 
    - `POST /papers` - to get the summary of the paper.
    - `POST /tables` - to get the tables from the paper.
```
curl -X POST \
  http://localhost:8000/papers \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://pubmed.ncbi.nlm.nih.gov/39327512/"
  }'
```










