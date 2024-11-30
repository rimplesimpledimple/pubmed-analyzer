# PDF content analysis prompts
PDF_SUMMARY_PROMPT = """Based on the content of the research paper, please generate a concise summary (around 250 words) focusing on the paper's objectives, 
methods, and key findings."""

PDF_MAIN_TABLE_PROMPT = """Given your understanding of the paper, return the table number that appears to be the main results table. Return 'none' if no table appears to be the main results table.
Output should be in JSON format.

If no table is found, return:
{
    "main_table": "none"
}

If a table is found, return:
{
    "main_table": table as JSON 
}
"""

# Text-based paper analysis prompts
TXT_PAPER_SUMMARY_PROMPT = """You are given an academic research paper as follows:

Title: {title}

Abstract: {abstract}

Pages with content in the following format:
Page 1: 
<Page Content>
Page 2: 
<Page Content>
...

Content of the paper:
{content}


Based on the content of the research paper, please generate a concise summary (around 250 words) focusing on the paper's objectives, 
methods, and key findings.
"""

TXT_PAPER_TABLE_PROMPT = """Given the following research paper:

Title: {title}
Abstract: {abstract}
Content: {content}

Identify the table that appears to be the main results table. Return your response in JSON format.

Note: Include the complete table content including headers, rows, and any footnotes."""