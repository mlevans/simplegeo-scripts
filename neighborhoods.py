from Credentials import *
from sys import argv
import simplegeo.context as context
from itertools import ifilter
import json as simplejson

def conv_decimal_to_string(decimal):
    """Converting SimpleGeo's lat/long Decimals to strings
    
      Keyword arguments:
      decimal -- A decimal value that is returned from SimpleGeo's Context API
    """
    try:
      return "%.5f" % (decimal,)
    except Exception,  e:
      #print "problem",decimal, e, e.__class__
      return None
      
def conv_coords_to_list_of_strings(neighborhood_boundary):
  """Creating a list of converted neighborhood coordinates
    
    Keyword arguments:
    neighborhood_boundary -- Coordinates/Vertices of a Neighborhood according to SimpleGeo's Context API. It is a list.
  """  
  coordinates = []
  
  for i in range(len(neighborhood_boundary[0])):
    coordinates.append([conv_decimal_to_string(neighborhood_boundary[0][i][0]),conv_decimal_to_string(neighborhood_boundary[0][i][1])])
    
  return coordinates
  
def create_geojson_for_neighborhoods(city,file_name):
  """
  Creating GeoJSON from data from SimpleGeo's API
  
  Keyword arguments:
  city -- The city from which you want neighborhoods
  file_name -- The name you want for your output file e.g., output_boston.json
  """
  print 'Connecting to the SimpleGeo Context API.'
  #initialize client with: client = context.Client('Your-Key','Your-Secret')
  client = context.Client(credentials['key'],credentials['secret'])
  #city data
  cities = {'boston':{'lat':42.332,'lon':-71.0202},'san francisco':{'lat':37.7599,'lon':-122.437}}
  
  if city in cities:
    #get lat and lon for the city
    lat = cities[city.lower()]['lat']
    lon = cities[city.lower()]['lon']
  else:
    print "We don't have the coordinates of your city in our data yet!"
    lat = float(raw_input("What is the latitude of the city?"))
    lon = float(raw_input("What is the longitude of the city?"))
    #return
  
  city = client.get_context(lat, lon)
  
  city_polygon = next(ifilter(lambda feature: feature['classifiers'][0]['category'] == 'Municipal', city['features']), None)
  
  bounds = city_polygon['bounds']
  
  northeast_lon,southwest_lat,southwest_lon,northeast_lat = bounds
  
  city_neighborhoods = client.get_context_from_bbox(southwest_lat,southwest_lon,northeast_lat,northeast_lon, features__category='Neighborhood')
  
  #start building the GeoJSON for the Neighborhoods
  neighborhoods = {"type": "FeatureCollection", "features": []}
  
  print 'Processing Neighborhoods.'
  
  for hood in city_neighborhoods['features']:
    hood_feature = client.get_feature(hood['handle'])
    neighborhood_boundaries = hood_feature.to_dict()['geometry']['coordinates']
    neighborhood_name = hood['name']
    neighborhood_boundary = hood_feature.to_dict()['geometry']['coordinates']
    #Building the GeoJson, neighborhood by neighborhood
    neighborhoods["features"].append({"type": "Feature", "geometry":{"type": "Polygon","coordinates":[conv_coords_to_list_of_strings(neighborhood_boundary)]},"properties":{"name":neighborhood_name}})
  
  #put the data in a file
  print 'Putting your data in a file.'
  output = open(file_name,'w')
  simplejson.dump(neighborhoods,output)
  output.close()
  
  print 'All done!'

if __name__ == '__main__':
  """
  Pass the name of the city and the name of your output file on the command line.
  """
  script,city,file_name = argv
  create_geojson_for_neighborhoods(city,file_name)