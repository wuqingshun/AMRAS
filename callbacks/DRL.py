import pandas as pd
import pathlib
from plotly import subplots as splt
import plotly.graph_objs as go
from dash import dcc,html
import math
import os

from dash.dependencies import Input, Output, State, ClientsideFunction
import feffery_antd_components as fac

from server import app

# get relative data folder
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

data_df=pd.read_csv(DATA_PATH.joinpath("loss_q.csv"))
steps=data_df['step']

train_losses=data_df['train_loss']
train_q_target=data_df['train_q_target']
train_q_evel=data_df['train_q_evel']


names = [
    "step",
    "train accuracy",
    "val accuracy",
    "train cross entropy",
    "val cross entropy",
]


@app.callback(
    Output("interval-simulated-step", "n_intervals"),
    [
        Input("DRL_algorithm", "value"),
        Input("DRL_layer", "value"),
        Input("interval-simulated-step", "n_intervals"),
        State("suspend_flag","value"),
        State("restore_button", "disabled"),
    ],
)
def update_interval_simulated_step(algorithm,layer,n_interval,suspend_flag,restore_state):
    '''
    After the data source changes, reset the step counter, after a pause, prevent n_intervals from changing
    :param algorithm:
    :param layer:
    :param suspend_flag:
    :param n_interval:
    :return:
    '''
    if suspend_flag!=None and suspend_flag!="":
        if restore_state:
            return 0
        else:
            return n_interval
    else:
        if restore_state:
            return 0
        else:
            return n_interval-1


@app.callback(
    Output("storage-simulated-run", "data"),
    [Input("interval-simulated-step", "n_intervals")],
    [
        State("DRL_algorithm", "value"),
        State("DRL_layer", "value"),
    ],
)
def simulate_run(n_intervals, algorithm, layer):
    '''
    Load data in real time based on step counter
    :param n_intervals:
    :param algorithm:
    :param layer:
    :return:
    '''

    if algorithm and layer and n_intervals > 0:

        step = n_intervals * 5
        #Select data source based on DRL algorithm and number of layers
        run_logs=data_df

        run_below_steps = run_logs[run_logs["step"] <= step]
        json = run_below_steps.to_json(orient="split")

        return json


@app.callback(
    Output("run-log-storage", "data"),
    [Input("interval-log-update", "n_intervals")],
    [State("storage-simulated-run", "data")],
)
def get_run_log(_, simulated_run):
    if simulate_run:
        return simulated_run

@app.callback(
    Output("start_button", "disabled"),
    [Input("DRL_algorithm", "value"),
     Input("DRL_layer", "value"),
     Input("loss_speed", "value"),
     Input("graph_flag", "value")
     ],
)
def start_state(algorithm,layer,speed,graph_flag):
    '''
    Only when the three input boxes of algorithm, level, and speed have values, can start
    :param algorithm:
    :param layer:
    :param speed:
    :return:
    '''
    if graph_flag==None or graph_flag=="":
        return True

    if algorithm!=None and layer!=None and speed!=None:
        return False

    return True

@app.callback(
    [
        Output("start_button", "nClicks"),
        Output("restore_button", "nClicks"),
        Output("suspend_button", "disabled"),
        Output("restore_button", "disabled"),
        Output("DRL_algorithm", "disabled"),
        Output("DRL_layer", "disabled"),
        Output("loss_speed", "disabled"),
        Output("graph_flag", "value"),
        Output("interval-simulated-step","disabled"),
        Output("interval-log-update","disabled"),
        Output("update_network_button","disabled")
     ],
    [
        Input("start_button", "nClicks"),
        Input("restore_button", "nClicks"),
        Input("loss_speed", "value"),
     ],
)
def other_button_state(start_clicks,restore_clicks,loss_speed):
    '''
    When the start button is clicked, the three input boxes and the start button become uneditable, and the pause (speed is not No) and reset buttons become editable
    :param n_clicks:
    :return:
    '''
    if restore_clicks:
        return 0,0,True, True, False, False, False, "no_load",True,True,True

    if start_clicks and loss_speed=="no":
        return 0,0,True,False,True,True,True,None,True,True,False
    elif start_clicks:
        return 0, 0, False, False, True, True, True, None,False,False,False

    return 0,0,True, True, False, False, False, "no_load",True,True,True

@app.callback(
    Output("suspend_flag", "value"),
    [Input("suspend_button", "nClicks"),
     Input("restore_button", "disabled"),
     State("suspend_flag", "value")

     ],
)
def switch_suspend_state(n_click,restore_state,suspend_flag):
    '''
    Update pause flag
    :param n_click:
    :param suspend_flag:
    :return:
    '''
    if restore_state:
        return None

    if suspend_flag=="" or  suspend_flag==None:
        return "suspend"
    return None

@app.callback(
    Output("interval-log-update", "interval"),
    [Input("loss_speed", "value")],
)
def update_interval_log_update(interval_rate):
    if interval_rate == "fast":
        return 500

    elif interval_rate == "regular":
        return 1000

    elif interval_rate == "slow":
        return 5 * 1000

    # Refreshes every 24 hours
    elif interval_rate == "no":
        return 24 * 60 * 60 * 1000

@app.callback(
    Output("loss_graph","figure"),
    [
        Input("graph_flag", "value"),
        Input("radio-display-mode-loss", "value"),
        Input("checklist-smoothing-options-loss", "value"),
        Input("slider-smoothing-loss", "value"),
        Input("loss_speed", "value"),
        Input("run-log-storage", "data"),
    ],
)
def update_loss_figure(graph_flag,display_mode, checklist_smoothing_options, slider_smoothing,loss_speed,run_log_json):
    '''
    Update the loss&reward graph
    :param graph_flag:
    :param display_mode:
    :param checklist_smoothing_options:
    :param slider_smoothing:
    :param loss_speed:
    :param run_log_json:
    :return:
    '''

    if loss_speed=="no":
        figure = update_graph(
            display_mode,
            checklist_smoothing_options,
            slider_smoothing,
            graph_flag,
            loss_speed,
            data_df
        )
    else:
        figure = update_graph(
            display_mode,
            checklist_smoothing_options,
            slider_smoothing,
            graph_flag,
            loss_speed,
            run_log_json
        )

    return figure


def update_graph(
    display_mode,
    checklist_smoothing_options,
    slider_smoothing,
    graph_flag,
    loss_speed,
    figure_data
):
    """
    :param graph_id: ID for Dash callbacks
    :param graph_title: Displayed on layout
    :param y_train_index: name of column index for y train we want to retrieve
    :param y_val_index: name of column index for y val we want to retrieve
    :param run_log_json: the json file containing the data
    :param display_mode: 'separate' or 'overlap'
    :param checklist_smoothing_options: 'train' or 'val'
    :param slider_smoothing: value between 0 and 1, at interval of 0.05
    :return: dcc Graph object containing the updated figures
    """

    def smooth(scalars, weight=0.6):
        last = scalars[0]
        smoothed = list()
        for point in scalars:
            smoothed_val = last * weight + (1 - weight) * point
            smoothed.append(smoothed_val)
            last = smoothed_val
        return smoothed

    layout = go.Layout(
        title='',
        margin=go.layout.Margin(l=50, r=50, b=50, t=50),
        # yaxis={"title": yaxis_title},
    )
    if loss_speed!="no":
        if figure_data!=None:
            figure_data = pd.read_json(figure_data, orient="split")
        else:
            figure = go.Figure(data=[], layout=layout)
            return figure

    if graph_flag==None or graph_flag=="":

        step = steps
        y_loss = figure_data['train_loss']
        q_target = figure_data['train_q_target']
        q_evel = figure_data['train_q_evel']

        # Apply Smoothing if needed
        if "loss" in checklist_smoothing_options:
            y_loss = smooth(y_loss, weight=slider_smoothing)

        if "q_value" in checklist_smoothing_options:
            q_target = smooth(q_target, weight=slider_smoothing)
            q_evel = smooth(q_evel, weight=slider_smoothing)

        # line charts
        trace_loss = go.Scatter(
            x=step,
            y=y_loss,
            mode="lines",
            name="Loss",
            line=dict(color="rgb(248, 196, 113 )"),
            showlegend=False,
        )

        trace_q_target= go.Scatter(
            x=step,
            y=q_target,
            mode="lines",
            name="Q-Target",
            yaxis='y2',
            line=dict(color="rgb(130, 224, 170 )"),
            showlegend=False,
        )
        trace_q_evel= go.Scatter(
            x=step,
            y=q_evel,
            mode="lines",
            name="Q-Eval",
            yaxis='y2',
            line=dict(color="rgb(230, 124, 70 )"),
            showlegend=False,
        )

        if display_mode == "separate_vertical":
            figure = splt.make_subplots(rows=3, cols=1, print_grid=False)

            figure.append_trace(trace_loss, 1, 1)
            figure.append_trace(trace_q_target, 2, 1)
            figure.append_trace(trace_q_evel, 3, 1)

            figure["layout"].update(
                title=layout.title,
                margin=layout.margin,
                scene={"domain": {"x": (0.0, 0.5), "y": (0.5, 1)}},
            )

            figure["layout"]["yaxis1"].update(title="Loss")
            figure["layout"]["yaxis2"].update(title="Q-Target")
            figure["layout"]["yaxis3"].update(title="Q-Eval")

        elif display_mode == "separate_horizontal":
            figure = splt.make_subplots(
                rows=1, cols=3, print_grid=False, shared_xaxes=True
            )

            figure.append_trace(trace_loss, 1, 1)
            figure.append_trace(trace_q_target, 1, 2)
            figure.append_trace(trace_q_evel, 1, 3)

            figure["layout"].update(title=layout.title, margin=layout.margin)
            figure["layout"]["yaxis1"].update(title="Loss")
            figure["layout"]["yaxis2"].update(title="Q-Target")
            figure["layout"]["yaxis3"].update(title="Q-Eval")

        elif display_mode == "overlap":
            #set the first coordinate
            layout['yaxis'] = dict(
                color="rgb(214, 137, 16 )",
                title="Loss"
            )
            # set the second y coordinate
            layout['yaxis2'] = dict(
                overlaying='y',
                side='right',
                # color= "rgb(35, 155, 86)",
                title="Q-Value"
            )
            figure = go.Figure(data=[trace_loss, trace_q_target,trace_q_evel], layout=layout)

        else:
            figure = go.Figure(data=[], layout=layout)
        return figure

    figure = go.Figure(data=[], layout=layout)
    return figure

#------------------------Neural Network Visualization-------------------------------
import util.nn_config as config
from util.nn_vis import *

@app.callback([Output("n_text_size","value"),
               Output("n_text_color_layer", "value"),
               Output("n_line_color_layer","value"),
               Output("n_text_color_feature_map", "value"),
               Output("n_line_color_feature_map","value"),
               Output("n_bounding_box_margin","value"),
               Output("n_inter_layer_margin","value"),
               Output("n_text_margin","value"),
               Output("n_input", "value"),
               Output("n_conv1", "value"),
               Output("n_conv2", "value"),
               Output("n_conv3", "value"),
               Output("n_pool1", "value"),
               Output("n_pool2", "value"),
               Output("n_fc1", "value"),
               Output("n_fc2", "value"),
               ],
              [Input("graph_flag", "value")])
def update_network_parameters(graph_flag):
    '''
    Update network parameters
    :param graph_flag:
    :return:
    '''

    if graph_flag == None or graph_flag == "":
        return str(config.text_size),str(config.text_color_layer),str(config.line_color_layer),\
               str(config.text_color_feature_map),str(config.line_color_feature_map),str(config.bounding_box_margin),\
               str(config.inter_layer_margin),str(config.text_margin),str(config.input),str(config.conv1),str(config.conv2), \
               str(config.conv3),str(config.pool1),str(config.pool2),str(config.fc1),str(config.fc2)

    return None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,

@app.callback(Output("network_div","children"),
              [Input("graph_flag", "value"),
               State("DRL_algorithm", "value"),
               State("DRL_layer", "value"),
               State("n_text_size","value"),
               State("n_text_color_layer", "value"),
               State("n_line_color_layer","value"),
               State("n_text_color_feature_map", "value"),
               State("n_line_color_feature_map", "value"),
               State("n_bounding_box_margin", "value"),
               State("n_inter_layer_margin", "value"),
               State("n_text_margin", "value"),
               State("n_input", "value"),
               State("n_conv1", "value"),
               State("n_conv2", "value"),
               State("n_conv3", "value"),
               State("n_pool1", "value"),
               State("n_pool2", "value"),
               State("n_fc1", "value"),
               State("n_fc2", "value"),
               Input("update_network_button","nClicks")])
def load_network_graph(graph_flag,alg,layer,n_text_size,n_text_color_layer,
                       n_line_color_layer,n_text_color_feature_map,
                       n_line_color_feature_map,n_bounding_box_margin,
                       n_inter_layer_margin,n_text_margin,n_input,
                       n_conv1,n_conv2,n_conv3,n_pool1,n_pool2,n_fc1,n_fc2,
                       update_network_button):
    '''
    Load preset network structure diagram
    :param graph_flag:
    :param layer:
    :return:
    '''
    network_svg=None
    if graph_flag == None or graph_flag == "":
        if update_network_button:
            #Edit network parameters
            config.text_size=int(n_text_size)
            config.text_color_layer=n_text_color_layer
            config.line_color_layer = n_line_color_layer
            config.text_color_feature_map = n_text_color_feature_map
            config.line_color_feature_map = n_line_color_feature_map
            config.bounding_box_margin = int(n_bounding_box_margin)
            config.inter_layer_margin = int(n_inter_layer_margin)
            config.text_margin = int(n_text_margin)
            config.input=n_input
            config.conv1 = n_conv1
            config.conv2 = n_conv2
            config.conv3 = n_conv3
            config.pool1 = n_pool1
            config.pool2 = n_pool2
            config.fc1 = n_fc1
            config.fc2 = n_fc2

            #Redraw the network structure diagram
            draw_network(alg+"_"+layer)
        #Determine the network structure path
        network_svg="img/"+alg+"_"+layer+".svg"
    if network_svg == None:
        return fac.AntdEmpty(description='Please click the start button to view the structure',
                             style={"margin-top": "40px"})

    #Determine whether the network structure exists (Modify it to your own absolute path)
    img_path="/Users/wuqingshun/PycharmProjects/AMSAS-code(github)/assets/img/"+alg+"_"+layer+".svg"
    if os.path.exists(img_path):
        return html.Img(src=app.get_asset_url(network_svg),className='twelve columns',style={"height":"80%"})
    else:
        return fac.AntdEmpty(description='The structure does not exist. Please click Update to create it',style={"margin-top":"40px"})







