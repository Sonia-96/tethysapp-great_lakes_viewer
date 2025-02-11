import json
from pathlib import Path
import requests
import pandas as pd
from tethys_sdk.routing import controller
from tethys_sdk.layouts import MapLayout
from .app import GreatLakesViewer as app


@controller(name='home', app_workspace=True)
class GreatLakesViewer(MapLayout):
    app = app
    base_template = 'great_lakes_viewer/base.html'
    map_title = 'Great Lakes Viewer'

    basemaps=["OpenStreetMap", "ESRI"]
    default_map_extent = [-95.48678973290308, 39.469776324236335, -71.79882218561728, 51.10826350669163]
    show_properties_popup = True
    plot_slide_sheet = True
    
    def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
        """
        Add layers to the map
        """
        
        # Load GeoJSON from files
        geojson_dir = Path(app_workspace.path) / 'geojson'
        path = geojson_dir / 'NewPoints.geojson'
        with open (path) as file:
            geojson = json.loads(file.read())
            geojson_layer = self.build_geojson_layer(
                geojson=geojson,
                layer_name=f'Points',
                layer_title=f'Points',
                layer_variable='point',
                visible=True,
                selectable=True,
                plottable=True
            )
        
        # Create layer groups
        layer_groups = [
            self.build_layer_group(
                id='points',
                display_name='20 Points',
                layer_control='checkbox',  # 'checkbox' or 'radio'
                layers=[geojson_layer]
            )
        ]

        return layer_groups
    
    @classmethod
    def get_vector_style_map(cls):
        return {
            'Point': {'ol.style.Style': {
                'image': {'ol.style.Circle': {
                    'radius': 5,
                    'fill': {'ol.style.Fill': {
                        'color': 'white',
                    }},
                    'stroke': {'ol.style.Stroke': {
                        'color': 'red',
                        'width': 3
                    }}
                }}
            }}
        }
        
    def get_plot_for_layer_feature(self, request, layer_name, feature_id, layer_data, feature_props, app_workspace,
                                *args, **kwargs):
        """
        Retrieves plot data for given feature on given layer.

        Args:
            layer_name (str): Name/id of layer.
            feature_id (str): ID of feature.
            layer_data (dict): The MVLayer.data dictionary.
            feature_props (dict): The properties of the selected feature.

        Returns:
            str, list<dict>, dict: plot title, data series, and layout options, respectively.
        """
        
        reach_id = feature_props.get('ReachID')
        url = f'https://api.water.noaa.gov/nwps/v1/gauges/{reach_id}/stageflow'
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Parse JSON response
            df_observed = pd.DataFrame(data['observed']['data'])
            df_forecast = pd.DataFrame(data['forecast']['data'])
            data = [
                {
                    'name': 'Observed',
                    'mode': 'lines',
                    'x':df_observed['validTime'].to_list(),
                    'y': df_observed['primary'].to_list()
                },
                {
                    'name': 'Forecast',
                    'mode': 'lines',
                    'x':df_forecast['validTime'].to_list(),
                    'y': df_forecast['primary'].to_list()
                }
            ]
            layout = {
                'yaxis': {
                    'title': 'Stage (feet)'
                }, 
                'xaxis': {
                    'title': 'Time'
                }
            }
            return f'Data - {reach_id}', data, layout
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
            return None, None, None
