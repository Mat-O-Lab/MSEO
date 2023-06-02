from rdflib import BNode, URIRef, Literal, Graph, Namespace
from rdflib.collection import Collection
from rdflib.util import guess_format
from rdflib.namespace import RDF, XSD, RDFS, OWL, SKOS, DCTERMS
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urlparse, unquote

from re import sub

import os
dir=os.path.dirname(os.path.realpath(__file__))
bfo2020_url='http://purl.obolibrary.org/obo/bfo/2020/bfo.owl'
util_url="https://purl.matolab.org/mseo/mid/util/"
BFO = Namespace(bfo2020_url+"/")
OBO = Namespace('http://purl.obolibrary.org/obo/')
MSEO = Namespace('https://purl.matolab.org/mseo/mid/')
UTIL = Namespace(util_url)
IOFAV = Namespace('https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/')


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

def add_ontology_header(g):
    g.bind('owl',OWL)
    g.bind('bfo',BFO)
    g.bind('obo',OBO)
    g.bind('mseo',MSEO)
    g.bind('skos',SKOS)
    g.bind('dcterms',DCTERMS)
    g.bind('iof-av',IOFAV)
    g.bind('',UTIL)
    g.add((URIRef(util_url),RDF.type,OWL.Ontology))
    g.add((URIRef(util_url),DCTERMS.abstract,Literal("This Ontology is a helper creating readable iri for all bfo object properties in by creating equivalent properties with snake case iri from there labels.",lang="en")))
    g.add((URIRef(util_url),DCTERMS.contributor,Literal("Thomas Hanke, Fraunhofer IWM",lang="en")))
    g.add((URIRef(util_url),DCTERMS.creator,Literal("Thomas Hanke, Fraunhofer IWM",lang="en")))
    g.add((URIRef(util_url),DCTERMS.license,Literal("http://opensource.org/licenses/MIT",datatype=XSD.anyURI)))
    g.add((URIRef(util_url),RDFS.label,Literal("Snake Case BFO Object Properties",lang="en")))
    return g

g=Graph()
bfo=parse_graph(bfo2020_url,g, format='xml')
out=Graph()

for property in bfo[: RDF.type : OWL.ObjectProperty]:
    label=next(bfo[property: RDFS.label : ],None)
    iri=URIRef(UTIL+snake_case(label))
    out=add_ontology_header(out)
    out.add((iri,RDF.type,OWL.ObjectProperty))
    out.add((property,OWL.equivalentProperty,iri))
    out.add((iri,RDFS.label,label))
out.serialize(dir+'/snake_case_bfo_iris.ttl',format='turtle')

