from typing import List
import re
from sec_filings import SECExtractor
import concurrent.futures
from functools import partial
from prepline_sec_filings.fetch import get_cik_by_ticker
import requests
from prepline_sec_filings.fetch import (
    get_form_by_ticker, open_form_by_ticker, get_filing
)
def sec_main(ticker:str,year:str,forms:List[str] = ['10-K','10-Q']):
    cik = get_cik_by_ticker(ticker)
    rgld_cik = int(cik.strip('0'))
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
    
    form_lists = []
    filings = json_data['filings']
    recent_filings = filings['recent']
    for acc_num,form_name,filing_date,report_date in zip(recent_filings['accessionNumber'],recent_filings['form'],recent_filings['filingDate'],recent_filings['reportDate']):
        if form_name in forms and filing_date.startswith(str(year)):
            no_dashes_acc_num = re.sub("-","",acc_num)
            form_lists.append([no_dashes_acc_num,form_name,filing_date,report_date])
    
    acc_nums_list = [l[0] for l in form_lists]

    get_filing_partial = partial(get_filing,
                                 cik=rgld_cik,
                                company='Unstructured Technologies', 
                                email='support@unstructured.io')
    
    sec_extractor = SECExtractor(ticker=ticker)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(get_filing_partial, acc_nums_list)
    results_texts = []
    for res in results:
        results_texts.append(res)
    assert len(results_texts) == len(acc_nums_list), f"The scraped text {len(results_texts)} is not matching with accession number texts {len(acc_nums_list)}"
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(sec_extractor.get_section_texts_from_text,results_texts)
    section_texts = []
    for res in results:
        section_texts.append(res)
    assert len(section_texts) == len(acc_nums_list), f"The section text {len(section_texts)} is not matching with accession number texts {len(acc_nums_list)}"

    for idx,val in enumerate(form_lists):
        val.append(section_texts[idx])
    return form_lists
    