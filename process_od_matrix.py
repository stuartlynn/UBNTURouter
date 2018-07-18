import requests
import pandas as pd
import argparse
import json
from tqdm import tqdm
from urllib.parse import urlencode
import numpy as np

class ODRunner():
    def __init__(self,
                 origin_file,
                 dest_file,
                 mode='pedestrian',
                 output_geo_file=None,
                 output_od_file=None,
                 server='http://valhalla:8002'):

        self.origin_file = origin_file
        self.dest_file = dest_file
        self.mode = mode
        self.output_geo_file = output_geo_file
        self.output_od_file = output_od_file
        self.server = server
        self.load_origins()
        self.load_destinations()
        self.run_routes()

    def run_routes(self,batch_size=50):
        result = []
        for index,origin in tqdm(self.origins.iterrows()):
            for batch, dests in self.destinations.groupby(np.arange(len(self.destinations))//batch_size):
                batch_result = self.make_request(origin,dests)
                result.append(pd.DataFrame( {'origin_lat': origin.latitude,
                                             'origin_lng': origin.longitude,
                                             'origin_id' : origin.id,
                                             'destination_lat': dests.latitude,
                                             'destination_lng': dests.longitude,
                                             'destination_id' : dests.id,
                                             'distance': [res['distance'] for res in  batch_result[0]],
                                             'time': [res['time'] for res in  batch_result[0]]}))
        pd.concat(result).to_csv(self.output_od_file,index=False)


    def make_request(self, origin, destinations):
        origin_array = [{'lon':origin.longitude,'lat':origin.latitude}]
        dests_array =  [{'lon':dest.longitude,'lat':dest.latitude} for index, dest in destinations.iterrows()]
        query_json = json.dumps({'sources': origin_array, 'targets': dests_array, 'costing' : self.mode})
        query_string= '{}/sources_to_targets?json={}'.format(self.server, query_json)
        result = requests.get(query_string).json()
        return result['sources_to_targets']

    def load_origins(self):
        self.origins = pd.read_csv(self.origin_file).head(200)
        print('Loaded ',len(self.origins),' origins ')

    def load_destinations(self):
        self.destinations = pd.read_csv(self.dest_file)
        print('Loaded ',len(self.destinations),' destinations')


if __name__ =='__main__':
    parser = argparse.ArgumentParser(description='Process OD matrixes from files in bulk')
    parser.add_argument('-i','--origins', help='origin file', default='/data/origins.csv')
    parser.add_argument('-d','--destinations', help='destination file',default='/data/destinations.csv')
    parser.add_argument('-g','--output_geo', help='output geometries')
    parser.add_argument('-od','--output_od', help='output od file', default='/data/od_matrix.csv')
    parser.add_argument('-m','--mode', default='auto', help="Mode of transit, 'car', 'bike', 'truck','walking'")

    args = parser.parse_args()
    OD = ODRunner(args.origins,
                  args.destinations,
                  mode=args.mode,
                  output_geo_file=args.output_geo,
                  output_od_file=args.output_od)


