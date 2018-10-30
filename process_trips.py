import requests
import pandas as pd
import argparse
import json
from tqdm import tqdm
from urllib.parse import urlencode
import numpy as np
import sys


class ODRunner():
    def __init__(self,
                 pairs_file,
                 # dest_file,
                 mode='pedestrian',
                 output_geo_file=None,
                 output_od_file=None,
                 server='http://valhalla:8002'):

        self.pairs_file = pairs_file
        self.mode = mode
        self.output_geo_file = output_geo_file
        self.output_od_file = output_od_file
        self.server = server

        #six degrees of precision in valhalla
        self.inv = 1.0 / 1e6;

        self.load_pairs()
        self.run_routes()

    def run_routes(self,batch_size=50):
        result = {
                "type": "FeatureCollection",
                "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
                "features": []}
        for index,pairs in tqdm(self.pairs.iterrows()):
                batch_result = self.make_request(pairs)
                result['features'].append( {'type':'Feature',
                                            'properties': {
                                                'origin_lat': pairs.origin_lat,
                                                 'origin_lng': pairs.origin_lng,
                                                 'origin_id' : pairs.origin_id,
                                                 'destination_lat': pairs.destination_lat,
                                                 'destination_lng': pairs.destination_lng,
                                                 'destination_id' : pairs.destination_id,
                                                 'sales': pairs.y_pred,
                                                 'distance': pairs.distance,
                                                 'sales_density_month': pairs.y_pred_density_monthly, 
                                                 'shape': str(batch_result['legs'][0]['shape']),
                                                 'time': str(batch_result['summary']['time']) 
                                             },
                                             'geometry':{
                                                "type": "LineString",
                                                "coordinates": self.decode_str(batch_result['legs'][0]['shape'])
                                                }
                                             })
        with open(self.output_geo_file, 'w') as outfile:
            json.dump(result, outfile)

    
    #decode an encoded string
    def decode_str(self,encoded):
        decoded = []
        previous = [0,0]
        i = 0
        #for each byte
        while i < len(encoded):
        #for each coord (lat, lon)
            ll = [0,0]
            for j in [0, 1]:
                shift = 0
                byte = 0x20
                #keep decoding bytes until you have this coord
                while byte >= 0x20:
                    byte = ord(encoded[i]) - 63
                    i += 1
                    ll[j] |= (byte & 0x1f) << shift
                    shift += 5
                #get the final value adding the previous offset and remember it for the next
                ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j] & 1 else (ll[j] >> 1))
                previous[j] = ll[j]
            #scale by the precision and chop off long coords also flip the positions so
            #its the far more standard lon,lat instead of lat,lon
            decoded.append([float('%.6f' % (ll[1] * self.inv)), float('%.6f' % (ll[0] * self.inv))])
        #hand back the list of coordinates
        return decoded


    def make_request(self, pairs):
        pairs_array = {'lon':pairs.origin_lng,'lat':pairs.origin_lat}
        dests_array =  {'lon':pairs.destination_lng,'lat':pairs.destination_lat}
        query_json = json.dumps({'locations':[pairs_array, dests_array], 'costing' : "pedestrian","directions_options":{"units":"miles"}})
        query_string= '{}/optimized_route?json={}'.format(self.server, query_json)
        result = requests.get(query_string).json()
        
        return result['trip']



    def load_pairs(self):
        self.pairs = pd.read_csv(self.pairs_file)
        print('Loaded ',len(self.pairs),' odpairs ')


if __name__ =='__main__':
    parser = argparse.ArgumentParser(description='Process OD matrixes from files in bulk')
    parser.add_argument('-i','--pairs', help='pairs file', default='/data/route_od.csv')
    parser.add_argument('-g','--output_geo', help='output geometries',default='/data/routes.geojson')
    parser.add_argument('-od','--output_od', help='output od file')
    parser.add_argument('-m','--mode', default='auto', help="Mode of transit, 'car', 'bike', 'truck','walking'")

    args = parser.parse_args()
    OD = ODRunner(args.pairs,
                  # args.destinations,
                  mode=args.mode,
                  output_geo_file=args.output_geo,
                  output_od_file=args.output_od)


