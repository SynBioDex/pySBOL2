#   Copyright (C) 2018 pysbolgraph developers. All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#   ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#   OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#   OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
from collections import defaultdict
from typing import Dict

from lxml import etree
from lxml.etree import tostring
from lxml.etree import QName

from rdflib.namespace import RDF
from rdflib import URIRef, Literal

rdfNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
sbolNS = "http://sbols.org/v2#"

# This is a module global that is used to register ownership relationships
# between classes. The serializer uses this to generate structured XML from
# flat RDF/XML
OWNERSHIP_PREDICATES: Dict[URIRef, set] = defaultdict(set)


def is_ownership_relation(triple, subject_type):
    # subject = triple[0]
    predicate = triple[1]
    # object = triple[2]

    return (predicate in OWNERSHIP_PREDICATES and
            subject_type in OWNERSHIP_PREDICATES[predicate])


def register_ownership_relation(parent_type, predicate):
    # Encapsulates and populates the OWNERSHIP_PREDICATES dictionary.
    #
    # :param parent_type: The RDF type of the parent class
    # :param predicate: The URI for the property.
    OWNERSHIP_PREDICATES[URIRef(predicate)].add(URIRef(parent_type))


def ns_prefix_dict(g):
    """Return a dictionary of namespace, uri prefix pairs."""
    return {ns: prefix.toPython() for (ns, prefix) in g.namespaces()}


def serialize_sboll2(g):
    prefixes = ns_prefix_dict(g)
    prefixes['rdf'] = rdfNS
    prefixes['sbol'] = sbolNS

    subject_to_element = dict()
    subject_to_type = dict()

    owned_elements = set()

    for triple in g.triples((None, RDF.type, None)):
        subject_to_type[triple[0]] = triple[2]
        subject = triple[0].toPython()
        the_type = triple[2].toPython()
        if subject in subject_to_element:
            etree.SubElement(subject_to_element[subject],
                             prefixify(RDF.type, prefixes, True),
                             attrib={
                                 QName(rdfNS, 'resource'): the_type
                             })
        else:
            subject_to_element[subject] = etree.Element(prefixify(the_type, prefixes,
                                                                  True),
                                                        attrib={
                                                            QName(rdfNS,
                                                                  'about'): subject
                                                        }
                                                        )

    for triple in g.triples((None, None, None)):
        if triple[1] == RDF.type:
            continue
        subject = triple[0].toPython()
        predicate = triple[1].toPython()
        obj = triple[2]
        element = subject_to_element[subject]
        if is_ownership_relation(triple, subject_to_type[triple[0]]):
            owned_element = subject_to_element[obj.toPython()]
            ownership_element = etree.SubElement(element,
                                                 prefixify(predicate, prefixes, True))
            ownership_element.append(owned_element)
            owned_elements.add(obj.toPython())
            continue
        if isinstance(obj, URIRef):
            etree.SubElement(element, prefixify(predicate, prefixes, True), attrib={
                QName(rdfNS, 'resource'): obj.toPython()
            })
        elif isinstance(obj, Literal):
            elem = etree.SubElement(element, prefixify(predicate, prefixes, True))
            elem.text = obj
        else:
            raise Exception()

    doc = etree.Element(QName(rdfNS, 'RDF'), nsmap=prefixes)

    for subject in subject_to_element:
        if subject not in owned_elements:
            element = subject_to_element[subject]
            doc.append(element)

    return tostring(doc, pretty_print=True)


def prefixify(iri, prefixes, create_new):
    for prefix in prefixes:
        prefix_iri = prefixes[prefix]
        if iri.startswith(prefix_iri):
            return QName(prefix_iri, iri[len(prefix_iri):])
    if not create_new:
        return iri
    fragment_start = iri.rfind('#')
    if fragment_start == -1:
        fragment_start = iri.rfind('/')
    if fragment_start == -1:
        return iri
    iri_prefix = iri[:fragment_start + 1]
    i = 0
    while True:
        prefix_name = 'ns' + str(i)
        if prefix_name not in prefixes:
            prefixes[prefix_name] = iri_prefix
            return QName(iri_prefix, iri[len(iri_prefix):])
        i = i + 1
