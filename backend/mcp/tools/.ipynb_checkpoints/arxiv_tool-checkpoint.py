import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict

def search_arxiv(query: str) -> List[Dict[str, str]]:
    """
    Queries the arXiv API for articles matching the search term.
    Returns a list of dicts containing Title, Summary, and Link.
    """
    safe_query = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{safe_query}&start=0&max_results=5"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            
        # Parse Atom feed XML
        root = ET.fromstring(xml_data)
        
        # XML namespaces used by arXiv API
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
        }
        
        results = []
        for entry in root.findall('atom:entry', namespaces):
            title_node = entry.find('atom:title', namespaces)
            summary_node = entry.find('atom:summary', namespaces)
            id_node = entry.find('atom:id', namespaces) # arXiv URL link
            
            title = title_node.text.strip() if title_node is not None else "Untitled"
            # Normalize newlines in title
            title = " ".join(title.split())
            
            summary = summary_node.text.strip() if summary_node is not None else "No summary available."
            summary = " ".join(summary.split())
            
            link = id_node.text.strip() if id_node is not None else ""
            
            results.append({
                "title": title,
                "summary": summary,
                "link": link
            })
            
        return results
    except Exception as e:
        return [{"title": "ArXiv Search Error", "summary": f"Could not retrieve research papers: {str(e)}", "link": ""}]
