import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

OSMFILE = "amsterdam_netherlands.osm"

postal_codes = re.compile(r'^1{1}0{1}\d{2} ?([a-z]{0}|[a-z]{2})$', re.IGNORECASE)
bad_postal_codes = []

def audit_postal_code(postal_code):
    postal_code = postal_code.split(';')[0].upper().replace(" ", "")
    if postal_codes.match(postal_code):
        return postal_code

    bad_postal_codes.append(postal_code)
    return None


def is_postal_code(address_key):
    return address_key == 'addr:postcode'

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]
ATTRIB = ["id", "visible", "amenity", "cuisine", "name", "phone"]


def shape_element(element):
    """
    Parse, validate and format node and way xml elements.
    Return list of dictionaries
    Keyword arguments:
    element -- element object from xml element tree iterparse
    """
    if element.tag == 'node' or element.tag == 'way':

        # Add empty created dictionary and k/v = type: node/way
        node = {'created': {}, 'type': element.tag}

        # Update pos array with lat and lon
        if 'lat' in element.attrib and 'lon' in element.attrib:
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]

        # Deal with node and way attributes
        for k in element.attrib:

            if k == 'lat' or k == 'lon':
                continue
            if k in CREATED:
                node['created'][k] = element.attrib[k]
            else:
                # Add direct key/value items of node/way
                node[k] = element.attrib[k]

        # Deal with second level tag items
        for tag in element.iter('tag'):
            k = tag.attrib['k']
            v = tag.attrib['v']

            # Search for problem characters in 'k' and ignore them
            if problemchars.search(k):
                # Add to array to print out later
                continue
            elif k.startswith('addr:'):
                address = k.split(':')
                if len(address) == 2:
                    if 'address' not in node:
                        node['address'] = {}
                    if is_postal_code(k):
                        v = audit_postal_code(v)
                        if v == None:
                            return None
                    node['address'][address[1]] = v
            else:
                node[k] = v

        # Add key/value node ref from way
        node_refs = []
        for nd in element.iter('nd'):
            node_refs.append(nd.attrib['ref'])

        if len(node_refs) > 0:
            node['node_refs'] = node_refs

        return node
    else:
        return None


def process_map(file_in, pretty=False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")


if __name__ == '__main__':
    process_map('amsterdam_netherlands.osm', False)
    print("Bad postal codes: ", len(bad_postal_codes))
