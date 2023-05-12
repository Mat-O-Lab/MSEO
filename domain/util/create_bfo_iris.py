from rdflib import BNode, URIRef, Literal, Graph, Namespace
from rdflib.collection import Collection
from rdflib.util import guess_format
from rdflib.namespace import CSVW, RDF, XSD, PROV, RDFS, OWL
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urlparse, unquote

from re import sub

import os
dir=os.path.dirname(os.path.realpath(__file__))

def snake_case(s):
  return '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()

def parse_graph(url: str, graph: Graph, format: str = '') -> Graph:
    """Parse a Graph from web url to rdflib graph object
    Args:
        url (AnyUrl): Url to an web ressource
        graph (Graph): Existing Rdflib Graph object to parse data to.
    Returns:
        Graph: Rdflib graph Object
    """
    parsed_url=urlparse(url)
    DATA = Namespace(url+"/")
    graph.bind('data',DATA)
    print(parsed_url)
    if not format:
        format=guess_format(parsed_url.path)
    if parsed_url.scheme in ['https', 'http']:
        graph.parse(parsed_url.geturl(), format=format)

    elif parsed_url.scheme == 'file':
        print(parsed_url.path)
        graph.parse(parsed_url.path, format=format)
    return graph

bfo2020_url='https://github.com/BFO-ontology/BFO-2020/raw/master/21838-2/owl/bfo-2020.owl'
g=Graph()
bfo=parse_graph(bfo2020_url,g, format='xml')
out=Graph()
BFO = Namespace(bfo2020_url+"/")
out.bind('owl',OWL)
out.bind('bfo',BFO)

predicate=OWL.equivalentProperty
for property in bfo[: RDF.type : OWL.ObjectProperty]:
    label=next(bfo[property: RDFS.label : ],None)
    iri=URIRef(bfo2020_url+'/'+snake_case(label))
    out.add((iri,predicate,property))

out.serialize(dir+'/snake_case_bfo_iris.ttl',format='turtle')