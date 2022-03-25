# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 10:55:33 2022

@author: yifei
"""

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np


app = Dash(__name__)

px.set_mapbox_access_token("pk.eyJ1IjoieWVtaS0yMyIsImEiOiJjbDEzZzl6MWswZWg5M2lzNmx4dGoza2U5In0.meLrG_2lR0ob4ZqA_ZGiPw")
df = pd.read_csv('test_path2.csv')
df.head()

time_col = 'timestep'

# Create figure
fig = px.scatter_mapbox(df,
          lat="lat" ,
          lon="lon",
          hover_name='type',
          color='type',
#               size = 'size',                            
          animation_frame=time_col,
          mapbox_style="basic",
          category_orders={
          time_col:list(np.sort(df[time_col].unique()))  
          },      
          width=1400,
          height=900,
          zoom=1)
 
app.layout = html.Div([
    dcc.Graph(
        id='test',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)