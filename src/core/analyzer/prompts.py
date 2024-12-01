# PDF content analysis prompts
PDF_SUMMARY_PROMPT = """Based on the content of the research paper, please generate a concise summary (around 250 words) focusing on the paper's objectives, 
methods, and key findings."""

PDF_MAIN_TABLE_PROMPT = """Given your understanding of the paper, return the table that appears to be the main results table. 
Do not make up any information. Only focus on the tables, not charts or other visual elements.
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

Identify and return the table that appears to be the main results table. Focus on the existing tables. Do not create tables that are not present in the paper.
"""