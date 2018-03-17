# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 21:03:34 2017

@author: Kaitlyn
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import folium
from matplotlib.colors import to_hex
import seaborn as sns

geology = gpd.read_file(r'C:\Users\Kaitlyn\Desktop\GIS\bedrock_geology\nhgeol_poly_dd.shp')

# take a selection of the columns to simplify the dataset
geology = geology.loc[:, ['geometry', 'ROCKTYPE1', 'ROCKTYPE2', 'UNIT_LINK']]

# use the USGS litho symbology text file for color styling
colors = pd.read_csv(r'C:\Users\Kaitlyn\Desktop\GeoPython\GeologyPython\lithrgb.txt', delimiter='\t')
colors.index = colors.text.str.lower()
colors.replace('-', '')
colors.head()

# use matplotlib's coloring and lambda function in python to join rgb values
colors['rgba'] = colors.apply(lambda x:'rgba(%s,%s,%s,%s)' % (x['r'],x['g'],x['b'], 255), axis=1)
colors['hex'] = colors.apply(lambda x: to_hex(np.asarray([x['r'],x['g'],x['b'],255]) / 255.0), axis=1)

# group the polygons by rock type
rock_group = geology.groupby('ROCKTYPE1')

# create folium maps for each rock type
map_center = [43.9,-72.6]
m = folium.Map(location=map_center, zoom_start=8, height='100%', control_scale=True)
fg = folium.FeatureGroup(name='Geology').add_to(m)


for rock in rock_group.groups.keys():
    rock_df = geology.loc[geology.ROCKTYPE1 == rock]
    style_function = lambda x: {'fillColor': colors.loc[x['properties']['ROCKTYPE1']]['hex'],
                                'opacity': 0, 
                                'fillOpacity': .85,
                               }
    g = folium.GeoJson(rock_df, style_function=style_function, name=rock.title())
    g.add_child(folium.Popup(rock.title()))
    fg.add_child(g)

folium.LayerControl().add_to(m)

# calculate area
geology['AREA_sqkm'] = geology.to_crs({'init': 'epsg:32616'}).area / 10**6

# get sum of all rock types
rock_group_sum = rock_group.sum()
rock_group_sum['ROCK'] = rock_group_sum.index

rock_group_sum.head()

# use seaborn to graph the instances of rock types
ax = sns.barplot(y='ROCK', x='AREA_sqkm', data=rock_group_sum)
fig = ax.get_figure(); fig.tight_layout()
fig.savefig('C:/Users/Kaitlyn/Desktop/GeoPython/GeologyPython/rock_types.png', dpi=100)


# create a folium map using USGS rock type descriptions
import requests

response = requests.request('GET', 'https://mrdata.usgs.gov/geology/state/json/{}'.format('MIYc;0')).json()
m = folium.Map(location=map_center, zoom_start=8, height='100%', control_scale=True)
fg = folium.FeatureGroup(name='Geology').add_to(m)

for unit in geology.groupby('UNIT_LINK').groups.keys():
    unit_df = geology.loc[geology.UNIT_LINK == unit]
    description = requests.request(
        'GET', 'https://mrdata.usgs.gov/geology/state/json/{}'.format(unit)).json()['unitdesc']
    style_function = lambda x: {'fillColor': colors.loc[x['properties']['ROCKTYPE1']]['hex'],
                                'opacity': 0, 
                                'fillOpacity': .85,
                               }
    g = folium.GeoJson(unit_df, style_function=style_function)
    g.add_child(folium.Popup(description))
    fg.add_child(g)

folium.LayerControl().add_to(m)
m

# Save as an html file, and then as a shapefile

m.save('C:/Users/Kaitlyn/Desktop/GeoPython/GeologyPython/geology_nh_map.html')

geology.to_file('C:/Users/Kaitlyn/Desktop/GeoPython/GeologyPython/geology.shp')
