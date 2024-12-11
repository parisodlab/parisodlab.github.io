import bibtexparser
import yaml
from datetime import datetime
from metapub import PubMedFetcher
from metapub.findit import FindIt
import requests
import os
from subprocess import Popen, PIPE

# Determine paths using Git
git_dir, err = Popen(['git', 'rev-parse', '--show-toplevel'], stdout=PIPE).communicate()
git_dir = git_dir.strip()
pubs_yaml = os.path.join(git_dir, b"_data/pubs_data.yaml")
pubs_list = os.path.join(git_dir, b"publications/publications_list.txt")


def BibtexFromDoi(doi):
    """Fetch BibTeX entry from DOI using the CrossRef API."""
    url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
    response = requests.get(url)
    response.raise_for_status()  # Ensure request was successful
    return response.text

def get_bibtex_to_dict(doi):
    """Get BibTex from DOI, parse a BibTeX entry, and return metadata as a dictionary."""
    try:
        bibtex_entry = BibtexFromDoi(doi)
        bib_database = bibtexparser.loads(bibtex_entry)
        if not bib_database.entries:
            return {"Error": "No entries found in the BibTeX string."}
        entry = bib_database.entries[0]
        dpub = {
            'Title': entry.get('title', '').strip("."),
            'Authors': entry.get('author', '').split(" and "),
            'DOI': entry.get('doi', ''),
            # Data_Published should be Year Month Day
            'Date_Published': " ".join([entry.get('year', ''), entry.get('month', ''), "1"]),
            'Journal': entry.get('journal', ''),
            'PMC': entry.get('pmc', ''),
            'PMID': entry.get('pmid', ''),
            'Abstract': entry.get('abstract', ''),
            'PDF': entry.get('url', '')
        }
        return dpub
    except Exception as e:
        return {"Error": str(e)}

def fetch_pmid(pmid):
    """Fetch metadata for a given PMID."""
    q = PubMedFetcher()
    src = FindIt(pmid)

    pub = q.article_by_pmid(pmid)
    if not pub:
        return {"Error": f"No article found for PMID {pmid}"}
    doi=pub.doi
    dpub = get_bibtex_to_dict(doi)
    return dpub

# Function to convert the date to a datetime object
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y %B %d")

def fetch_pubs_and_update_yaml(pub_list, pubs_yaml):
    """Fetch publications, check against existing YAML database, and update the file."""

    doc_list = []

    # Load current YAML file
    with open(pubs_yaml, 'r') as f:
        yaml_db = yaml.safe_load(f)

    existing_pmids = [str(x["PMID"]) for x in yaml_db if 'PMID' in x]
    existing_dois = [str(x["DOI"]) for x in yaml_db if 'DOI' in x]

    # Fetch new publications
    for i in pub_list:
        if i not in existing_pmids and i not in existing_dois:
            print(f"Fetching new publication: {i}")
            if i.startswith("10."):
                doc_list.append(get_bibtex_to_dict(i))
                print(doc_list)
            else:
                doc_list.append(fetch_pmid(i))
                print(doc_list)


    # Append existing entries to the list
    for entry in yaml_db:
        doc_list.append(entry)
    
    # Write the updated database back to the YAML file
    with open(pubs_yaml, 'w') as f:
        f.write(yaml.safe_dump(doc_list))

    # Sort the data based on the date_published field
    with open(pubs_yaml, 'r') as f:
        data = yaml.safe_load(f)
    data = sorted(data, key=lambda x: parse_date(x['Date_Published']), reverse=True)

    # Write updated database back to the YAML file
    with open(pubs_yaml, 'w') as f:
        f.write(yaml.safe_dump(data))



# Open the things to be updated from the publications.txt file
pub_list = map(str, open(pubs_list, 'r').read().splitlines()[1:])
fetch_pubs_and_update_yaml(pub_list, pubs_yaml)


