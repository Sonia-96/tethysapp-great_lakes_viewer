import json
from pathlib import Path
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
        lake_names = ['Superior', 'Michigan', 'Huron', 'StClair', 'Erie', 'Ontario']
        
        lake_layers = []
        for lake_name in lake_names:
            path = geojson_dir / f'Lake{lake_name}.geojson'
            with open(path) as file:
                geojson = json.loads(file.read())
                geojson_layer = self.build_geojson_layer(
                    geojson=geojson,
                    layer_name=f'Lake {lake_name}',
                    layer_title=f'Lake {lake_name}',
                    layer_variable=f'{lake_name}',
                    visible=True,
                    selectable=True,
                    plottable=True,
                    excluded_properties=['HYDRO_P_', 'UIDENT', 'NAMESP', 'NAMEFR', 'TYPE', 'NAMEEN'],
                )
                lake_layers.append(geojson_layer)
        
        # Create layer groups
        layer_groups = [
            self.build_layer_group(
                id='great-lakes',
                display_name='Great Lakes',
                layer_control='checkbox',  # 'checkbox' or 'radio'
                layers=lake_layers
            )
        ]

        return layer_groups
        
    @classmethod
    def get_vector_style_map(cls):
        return {
            'MultiPolygon': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': 'navy',
                    'width': 1
                }},
                'fill': {'ol.style.Fill': {
                    'color': 'rgba(0, 25, 128, 0.1)'
                }}
            }},
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
        
        data_directory = Path(app_workspace.path) / 'data'
        
        name = feature_props.get('NAMEEN')
        if 'Michigan' in name or 'Huron' in name:
            name = 'Lake Michigan-Huron'
        elif 'Clair' in name:
            name = 'Lake St.Clair'
        
        layout = {
            'yaxis': {
                'title': 'Water Level (feet)'
            }, 
            'xaxis': {
                'title': 'Month'
            }
        }
        
        output_path = data_directory / f'{name}.csv'
        
        df = pd.read_csv(output_path)
        data = [
            {
                'name': 'Water Levels',
                'mode': 'lines',
                'x': df['Month'].to_list(),
                'y': df.iloc[:, 1].to_list(),
                'line': {
                    'width': 2,
                    'color': 'blue'
                }
            },
        ]
        
        return f'Monthly Mean Water Levels - {name}', data, layout
