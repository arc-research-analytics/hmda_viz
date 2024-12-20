from bokeh.models import CategoricalColorMapper, LogColorMapper, ColorBar, BasicTicker, NumeralTickFormatter
from bokeh.palettes import Viridis6
from bokeh.plotting import figure
from bokeh.sampledata.unemployment import data as unemployment
from bokeh.sampledata.us_counties import data as counties
from bokeh.embed import file_html
import streamlit as st
import streamlit.components.v1 as components
from pyproj import Transformer
import pandas as pd
import geopandas as gpd

# set page configurations
st.set_page_config(
    page_title="HMDA Tool",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=":material/real_estate_agent:"
)

# the custom CSS lives here:
hide_default_format = """
    <style>
        .reportview-container .main footer {
            visibility: hidden;
        }    
        #MainMenu, header, footer {
           visibility: hidden;
        }
        div.stActionButton {
            visibility: hidden;
        }
        [class="stAppDeployButton"] {
            display: none;
        }
    </style>
"""

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)

# Step 1: Streamlit Title
st.title("Metro Atlanta Census Tracts")

# Step 2: Load the Geopackage File
# Replace 'your_file.gpkg' with the path to your geopackage file
gdf = gpd.read_file('../../Geographies/ARC_CTs.gpkg')

# Step 3: Filter Data for Metro Atlanta Area
st.write(gdf.head())

# Step 4: Convert Geometries to Web Mercator
# Convert geometries to EPSG:3857 (Web Mercator) for compatibility with Bokeh
gdf = gdf.to_crs(epsg=3857)

# Step 5: Extract Coordinates for Bokeh Patches
# Step 5: Extract Coordinates for Bokeh Patches
tract_xs = []
tract_ys = []

for geom in gdf.geometry:
    if geom.type == "Polygon":  # Single Polygon
        tract_xs.append(list(geom.exterior.coords.xy[0]))
        tract_ys.append(list(geom.exterior.coords.xy[1]))
    elif geom.type == "MultiPolygon":  # MultiPolygon
        for poly in geom.geoms:  # Iterate over each Polygon in the MultiPolygon
            tract_xs.append(list(poly.exterior.coords.xy[0]))
            tract_ys.append(list(poly.exterior.coords.xy[1]))

# Step 6: Create Bokeh Figure
p = figure(
    title="Metro Atlanta Census Tracts",
    x_axis_type="mercator",
    y_axis_type="mercator",
    active_scroll="wheel_zoom",
    active_drag="pan",
    toolbar_location="right",
    height=600,
    width=900
)

# Add basemap
p.grid.grid_line_color = None
p.hover.point_policy = "follow_mouse"
p.add_tile("CartoDB Voyager", retina=True)

# Add geometries as outlines
p.patches(
    tract_xs,
    tract_ys,
    fill_alpha=0.0,
    line_color="blue",
    line_width=0.8
)

# Step 7: Embed in Streamlit
html = file_html(p, resources="cdn")
components.html(html, height=700, width=1000)


# TEXAS EXAMPLE -V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V-V
# # Filter counties for Texas
# counties = {
#     code: county for code, county in counties.items() if county["state"] == "tx"
# }

# # Prepare data for the plot
# county_xs = [county["lons"] for county in counties.values()]
# county_ys = [county["lats"] for county in counties.values()]
# county_names = [county['name'] for county in counties.values()]
# county_rates = [unemployment[county_id] for county_id in counties]

# # Convert lat/lon to Web Mercator
# transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

# county_xs_mercator = [
#     [transformer.transform(lon, lat)[0]
#      for lon, lat in zip(county["lons"], county["lats"])]
#     for county in counties.values()
# ]
# county_ys_mercator = [
#     [transformer.transform(lon, lat)[1]
#      for lon, lat in zip(county["lons"], county["lats"])]
#     for county in counties.values()
# ]

# # Define bins and labels (categories) for unemployment rates
# bins = [0, 5, 10, 15, 20, 25, 30]
# labels = ['0-5%', '5-10%', '10-15%', '15-20%', '20-25%', '25-30%']

# # Discretize the rates into categories
# county_rates_categorized = pd.cut(
#     county_rates, bins=bins, labels=labels, right=False)

# # Convert to string for compatibility with CategoricalColorMapper
# county_rates_categorized = county_rates_categorized.astype(str)

# data = dict(
#     x=county_xs_mercator,
#     y=county_ys_mercator,
#     name=county_names,
#     rate=county_rates_categorized,  # Use categorized rates
# )

# # Example Data (Discrete categories for unemployment rate)
# categories = ['0-5%', '5-10%', '10-15%', '15-20%',
#               '20-25%', '25-30%']  # Adjust based on your data
# colors = Viridis6  # You can adjust this palette if you have more categories

# # Color mapper for scale
# color_mapper = CategoricalColorMapper(
#     palette=colors,
#     factors=categories
# )

# # Create the figure
# p = figure(
#     title=None,
#     x_axis_location=None,
#     y_axis_location=None,
#     x_axis_type="mercator",
#     y_axis_type="mercator",
#     tooltips=[
#         ("County Name", "@name"),
#         ("Unemployment Rate", "@rate"),
#     ],
#     active_scroll="wheel_zoom",  # Set wheel_zoom as the active tool
#     active_drag="pan",  # Set pan as the active drag tool
#     toolbar_location=None,
# )

# p.grid.grid_line_color = None
# p.hover.point_policy = "follow_mouse"
# p.add_tile("CartoDB Voyager", retina=True)

# # Add the patches (choropleth map)
# p.patches(
#     'x',
#     'y',
#     source=data,
#     fill_color={'field': 'rate', 'transform': color_mapper},
#     fill_alpha=0.85,
#     line_color="white",
#     line_width=0.5
# )

# # Add a color bar (legend for color scale)
# color_bar = ColorBar(
#     color_mapper=color_mapper,
#     width=20,
#     height=210,
#     location=(3, 3),
#     orientation='vertical',
#     title='Unemployment Rate by County (%)',
#     title_text_color='#000000',
#     ticker=BasicTicker(desired_num_ticks=len(colors) + 1),
#     formatter=NumeralTickFormatter(format="0"),
#     bar_line_color='#ffffff',
#     bar_line_width=2,
#     label_standoff=6,
#     background_fill_alpha=0.4,
#     background_fill_color='#ffffff',
#     major_label_text_color='#444444',
#     scale_alpha=1  # overall transparency of legend
# )

# p.add_layout(color_bar, 'center')

# # add title
# st.title('Choropleth Example')

# # Workaround to render Bokeh in Streamlit
# html = file_html(p, resources="cdn")
# components.html(html, height=600, width=1250)
