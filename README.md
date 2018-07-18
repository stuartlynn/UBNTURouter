# Uber (but not that Uber) Router

This is a little system for easily doing bulk OD pair calculations using Valhalla.


## Process tiles
We first need to load in a road network from OSM. There is script to make this easier included
in the repo. We can pull regions of OSM from the [Metro Extracts](https://metro-extracts.nextzen.org/#atlanta_georgia)
page from NextZen (where it lives after the disapearance of MapZen RIP). Simply place the names of the extracts you
want to load on seperate lines in the /config/tile\_sets.csv file. Then run

```bash
docker-compose run valhalla python3 fetch_and_generate_tiles.py
```

this will generate the tiles valhalla needs for routing.

## Run OD calculation

First we need to bring up the valhalla server so we run

```bash
docker-compose up valhalla
```
this will start the server running. Then we just need to run the processing script

```bash
docker-compose run procesisng python /data/process_od_matrix.py
```

this expects a file called origins.csv and destinations.csv to exist with a latitude, longitude and id column.

If all works, it will run through all the pairs and output an od\_matrix.csv file with the times and distances
between each origin and destination.

## To do

- [ ] Add batch routing
- [ ] Make the argments to the script actually do something
- [ ] Figure out a way to do this on multiple machines to speed up large jobs
