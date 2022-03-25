from callbacks.DRL import *
from dash import dcc,html
import dash_bootstrap_components as dbc
import feffery_antd_components as fac

DRL_page = html.Div([
        #Empty div, loading flags for cached graphs
        html.Div([fac.AntdInput(id="graph_flag",value="no_load",style={"display":"none"})]),
        #Empty div, pause flag for cached graphs
        html.Div([fac.AntdInput(id="suspend_flag",value="",style={"display":"none"})]),
        #The first line of Div (1*2) controller module and loss trend module
        html.Div([
            html.Div([
                    dcc.Store(id="storage-simulated-run", storage_type="memory"),
                    # Increment the simulation step count at a fixed time interval
                    dcc.Interval(
                        id="interval-simulated-step",
                        interval=125,  # Updates every 100 milliseconds, i.e. every step takes 25 ms
                        n_intervals=0,
                        disabled=True
                    ),
                    html.H6(
                        "Select a DRL algorithm",
                        className="card-title",
                        style={"font-weight":"400","font-size":"1.1em","color":"rgb(3, 67, 105)"}
                        ),


                    fac.AntdSelect(
                        id="DRL_algorithm",
                        placeholder='DRL algorithms',
                        options=[
                            {
                                'group': 'Value-based',
                                'options': [
                                    {'label': 'DQN', 'value': 'DQN'},
                                    {'label': 'Dueling DQN', 'value': 'Dueling DQN'},
                                ]
                            },
                            {
                                'group': 'Policy-based',
                                'options': [
                                    {'label': 'PPO', 'value': 'PPO'},
                                    {'label': 'DPPO', 'value': 'DPPO'}
                                ]
                            },
                            {
                                'group': 'Actor-critic',
                                'options': [
                                    {'label': 'A3C', 'value': 'A3C'},
                                    {'label': 'DDPG', 'value': 'DDPG'}
                                ]
                            }
                        ],
                        value="DQN",
                        disabled=False,
                        # style={'width':'300px'}
                        style={'width':'90%'}
                    ),
                    # html.Hr(),
                    html.H6(
                        "Select a layer parameters",
                        className="card-title",
                        style={"font-weight":"400","font-size":"1.1em","color":"rgb(3, 67, 105)"}
                        ),
                    fac.AntdSelect(
                        id="DRL_layer",
                        placeholder='layer parameters',
                        options=[
                            {'label': 'Conv:3; Pool:2; Fc:2', 'value': 'l1'},
                            {'label': 'Conv:2; Pool:1; Fc:2', 'value': 'l2'},
                            {'label': 'Conv:2; Pool:1; Fc:1', 'value': 'l3'}

                        ],
                        value="l1",
                        disabled=False,
                        style={'width':'90%'}
                    ),
                    html.H6(
                        "Select a update speed",
                        className="card-title",
                        style={"font-weight":"400","font-size":"1.1em","color":"rgb(3, 67, 105)"}
                        ),
                    fac.AntdSelect(
                        id="loss_speed",
                        placeholder='update speed',
                        options=[
                            {"label": "No Updates","value": "no",},
                            {
                                "label": "Slow Updates",
                                "value": "slow",
                            },
                            {
                                "label": "Regular Updates",
                                "value": "regular",
                            },
                            {
                                "label": "Fast Updates",
                                "value": "fast",
                            },
                        ],
                        value="no",
                        disabled=False,
                        style={'width':'90%'}
                    ),
                    dcc.Interval(id="interval-log-update", n_intervals=0,disabled=True),
                    dcc.Store(id="run-log-storage", storage_type="memory"),
                    html.Hr(),
                    html.Div([ fac.AntdButton('Start', shape='round',id="start_button",disabled=False)],
                        style={"text-align":"center","margin-bottom":"20px","padding-left":"10px","padding-right":"10px","float":"left"}
                             ),
                    html.Div([
                              fac.AntdButton('Suspend', shape='round', id="suspend_button",type="primary",danger=True,disabled=True),
                              ],
                             style={"text-align": "center", "margin-bottom": "20px", "padding-right": "10px","float":"left"}
                             ),
                    html.Div([
                              fac.AntdButton('Restore', shape='round', id="restore_button",danger=True,type='dashed',disabled=True)
                              ],
                             style={"text-align": "center", "margin-bottom": "20px", "padding-right": "10px","float":"left"}
                             )
                ],
                 className="pretty_container four columns",
                ),
            html.Div([
                html.H6(
                    "Loss & Q-Value",
                    className="card-title",
                    style={"font-weight": "700", "font-size": "1.4em", "color": "rgb(3, 67, 105)"}
                ),
                #loss trend chart
                html.Div([
                    html.Div([
                        # drawing mode
                        html.Div(
                            [
                                html.P(
                                    "Display Mode:",
                                    style={"font-weight": "bold", "margin-right": "10px", "display": "inline-block"},
                                    className="plot-display-text",
                                ),
                                html.Div(
                                    [
                                        dcc.RadioItems(
                                            options=[
                                                {
                                                    "label": " Overlapping",
                                                    "value": "overlap",
                                                },
                                                {
                                                    "label": " Vertical",
                                                    "value": "separate_vertical",
                                                },
                                                {
                                                    "label": " Horizontal",
                                                    "value": "separate_horizontal",
                                                },
                                            ],
                                            value="overlap",
                                            id="radio-display-mode-loss",
                                            labelStyle={'display': 'inline-block', "margin-right": "10px"},
                                            className="plot-display-radio-items",

                                        )
                                    ],
                                    className="radio-item-div",
                                ),
                                html.Div(id="div-current-loss-value"),
                            ],
                            className="entropy-div",
                            style={"display": "inline-block", "margin-bottom": "60px", }
                        ),
                        #Smoothing options
                        html.Div(
                            [
                                html.P(
                                    "Smoothing:",
                                    style={"font-weight": "bold", "margin-right": "10px","display":"inline-block"},
                                    className="plot-display-text",
                                ),
                                dcc.Checklist(
                                    options=[
                                        {"label": " Loss", "value": "loss"},
                                        {"label": " Q-Value", "value": "q_value"},
                                    ],
                                    value=[],
                                    id="checklist-smoothing-options-loss",
                                    className="checklist-smoothing",
                                    labelStyle={'display': 'inline-block', "margin-right": "10px"},
                                    # style={"display":"inline-block"}
                                ),
                            ],
                            style={"margin-left": "90px","display":"inline-block"},
                        ),

                        #smoothness
                        html.Div(
                            [
                                html.P(
                                    "Smoothing:",
                                    style={"font-weight": "bold", "margin-top": "-50px"},
                                    className="plot-display-text",
                                ),

                                #text prompt
                                fac.AntdTooltip(
                                    dcc.Slider(
                                        min=0,
                                        max=1,
                                        step=0.05,
                                        marks={i / 5: str(i / 5) for i in range(0, 6)},
                                        value=0.6,
                                        updatemode="drag",
                                        id="slider-smoothing-loss",
                                    ),
                                    title="smoothness"
                                )
                            ],
                            style={"margin-bottom": "40px"},
                            className="slider-smoothing",
                        ),
                    html.Hr(),

                    ],
                     className="twelve columns",
                     style={"padding-bottom": "0px","display":"inline-block"},
                     ),
                    # trend
                    dcc.Graph(id="loss_graph",className="twelve columns",
                              )
                    ],
                    className="container",
                    style={"margin-bottom": "0px"},
                    ),
                html.Hr(),

                #Neural network structure
                html.H6(
                        "Neural Network Structure",
                        className="card-title",
                        style={"font-weight": "700", "font-size": "1.4em", "color": "rgb(3, 67, 105)"}
                    ),
                html.Div([
                    html.Div(
                        [
                            # Adjust spacing and size parameters
                            html.Div([
                                html.Div(
                                    [
                                        fac.AntdCollapse(
                                            title='Network Parameters',
                                            is_open=False,
                                            children=[
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='input',
                                                        id='n_input',
                                                        style={
                                                            'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="height/width/depth"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='conv1',
                                                        id='n_conv1',
                                                        style={
                                                            'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="num filters/filter size/stride"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='conv2',
                                                        id='n_conv2',
                                                        style={
                                                             'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="num filters/filter size/stride"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='conv3',
                                                        id='n_conv3',
                                                        style={
                                                             'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="num filters/filter size/stride"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='pool1',
                                                        id='n_pool1',
                                                        style={
                                                             'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="filter size/stride"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='pool2',
                                                        id='n_pool2',
                                                        style={
                                                            'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="filter size/stride"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='fc1',
                                                        id='n_fc1',
                                                        style={
                                                             'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="num filters"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='fc2',
                                                        id='n_fc2',
                                                        style={
                                                             'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="num filters"
                                                ),

                                            ],
                                            style={"display":"inline-block","margin-left": "3px",},
                                        ),
                                        #folding panel
                                        fac.AntdCollapse(
                                            title='Size & Margin',
                                            is_open=False,
                                            children=[
                                                fac.AntdInput(
                                                    placeholder='no data',
                                                    addonBefore='text size',
                                                    id='n_text_size',
                                                    style={
                                                         'width': '50%',
                                                        'marginBottom': '5px'
                                                    }),
                                                fac.AntdInput(
                                                    placeholder='no data',
                                                    addonBefore='text margin',
                                                    id='n_text_margin',
                                                    style={
                                                         'width': '50%',
                                                        'marginBottom': '5px'
                                                    }),
                                                fac.AntdInput(
                                                    placeholder='no data',
                                                    addonBefore='inter layer margin',
                                                    id='n_inter_layer_margin',
                                                    style={
                                                         'width': '50%',
                                                        'marginBottom': '5px'
                                                    }),
                                                fac.AntdInput(
                                                    placeholder='no data',
                                                    addonBefore='bounding box margin',
                                                    id='n_bounding_box_margin',
                                                    style={
                                                         'width': '50%',
                                                        'marginBottom': '5px'
                                                    }),
                                            ],
                                            style={"display":"inline-block","margin-left": "3px",},
                                        ),
                                        fac.AntdCollapse(
                                            title='Color',
                                            is_open=False,
                                            children=[
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='text color layer',
                                                        id='n_text_color_layer',
                                                        style={
                                                             'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="R/G/B"
                                                    ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='line color layer',
                                                        id='n_line_color_layer',
                                                        style={
                                                            'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="R/G/B"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='line color feature map',
                                                        id='n_line_color_feature_map',
                                                        style={
                                                             'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="R/G/B"
                                                ),
                                                fac.AntdTooltip(
                                                    fac.AntdInput(
                                                        placeholder='no data',
                                                        addonBefore='text color feature map',
                                                        id='n_text_color_feature_map',
                                                        style={
                                                            'width': '50%',
                                                            'marginBottom': '5px'
                                                        }),
                                                    title="R/G/B"
                                                ),
                                            ],
                                        style={"display":"inline-block","margin-bottom": "20px","margin-left": "3px",},
                                        ),
                                    fac.AntdButton(
                                        [
                                            fac.AntdIcon(
                                                icon='md-update'
                                            ),
                                            'update'
                                        ],
                                        id='update_network_button',
                                        type='primary',
                                        disabled=False,
                                        style={"margin-left": "20px",},
                                    ),
                                ],
                                ),
                                ],
                                    className="entropy-div",
                                    style={"display":"inline-block"},
                                ),

                            ],
                        className="twelve columns",
                        style={"padding-bottom": "0%"},
                            ),
                    # Structure diagram
                    html.Div(id="network_div",className="twelve columns"),
                ],
                    className="container",
                    style={"margin-bottom": "0px"},
                ),
                ],
                className= "pretty_container ten columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
)

