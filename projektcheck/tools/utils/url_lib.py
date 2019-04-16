import urllib, urllib2
import json

GOOGLE_API = ("http://maps.googleapis.com/maps/api/geocode/json?address=" +
              "{zipcode},{city},{street}%20{number}")

def get_location(street, number, city, zipcode):
    url = GOOGLE_API.format(zipcode=zipcode,
                         city=urllib.quote_plus(city.encode('utf8')),
                         street=urllib.quote_plus(street.encode('utf8')),
                         number=number)

    response = urllib2.urlopen(url)
    res_json = json.load(response)
    address = u'{z} {c}, {s} {n}'.format(z=zipcode, c=city, s=street, n=number)   
    if 'results' not in res_json or len(res_json['results']) == 0:
        return None, 'Adresse ' + address + ' nicht gefunden'
    if len(res_json['results']) > 1:
        return None, 'Adresse ' + address + ' nicht eindeutig'
    result = res_json['results'][0]
    loc = result['geometry']['location']

    return (loc['lat'], loc['lng']), ''