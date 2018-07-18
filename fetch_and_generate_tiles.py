from urllib.request import urlretrieve
import subprocess
import os

def download_tile_sets():

    print('tile sets to load ', target_tile_sets)

    base_url = 'https://s3.amazonaws.com/metro-extracts.nextzen.org/2018-05-19-13-00'
    osm_path = '/data/osm'
    downloaded_targets = []
    for tile_set in tile_sets_to_load:
        target_path = "{osm_path}/{tile_set}".format(osm_path=osm_path, tile_set=tile_set.strip())
        if os.path.isfile(target_path)==False:
            print('downloading osm files for ', tile_set.strip())
            url = "{base_url}/{tile_set}".format(base_url=base_url, tile_set=tile_set.strip())
            print('downloading osm files for ', tile_set , ' from ', url)
            urlretrieve(url,
                        target_path)
        else :
            print('Found ',tile_set, ' already skipping download')
        downloaded_targets.append(target_path)
    return downloaded_targets

def get_list_of_tiles_to_load():
    with open('/conf/tile_sets.csv', 'r') as tile_file:
        target_tile_sets = tile_file.readlines()

    with open('/conf/loaded_tile_sets.csv', 'r') as loaded_file:
        loaded_tile_sets = loaded_file.readlines()

    tile_sets_to_load = list(set(target_tile_sets) - set(loaded_tile_sets))

    return [ tile +'.osm.pdf' for tile in tile_sets_to_load ]

if __name__ == "__main__":
    TILE_SET_LIST = get_list_of_tiles_to_load()
    download_tile_sets(TILE_SET_LIST)
    subprocess.call(['valhalla_build_tiles',
                     '-c',
                     '/conf/valhalla.json'
                    ]+ TILE_SET_LIST)
    subprocess.call(['tar',
                     '-cvf',
                     '/data/valhalla/tiles.tar',
                     '/data/vahalla/*'
                    ]+ TILE_SET_LIST)

