import dash_bootstrap_components as dbc
from callbacks.simulator import *

#---------------------------Page Layout------------------------------
simulator_page = html.Div(
    [
        #Two DIVs on the first line
        html.Div(
            [
                html.Div(
                    [
                        #Card layout
                        dbc.Card([
                            dbc.CardBody([
                                    html.H6(
                                            "Select time range in histogram",
                                            className="card-title",
                                            style={"font-weight":"350","font-size":"1.2em","color":"rgb(3, 67, 105)"}
                                            ),
                                    #time range selector
                                    dcc.RangeSlider(
                                        id="time_slider",
                                        min=1451606400,
                                        max=1451620800,
                                        value=[1451610000,1451615400],
                                        marks=time_marks,
                                        allowCross=False,
                                        tooltip={"always_visible": False, "placement": "bottom"},
                                      ),

                            ]),
                            dbc.CardBody([
                                    html.H6("Filter by task type", className="card-title",
                                            style={"font-weight": "350", "font-size": "1.2em",
                                                   "color": "rgb(3, 67, 105)"}),
                                    # html.Br(),
                                    dcc.RadioItems(
                                        id="task_type_selector",
                                        options=[
                                            {"label": "All ", "value": "all"},
                                            #Online: Emerging Unmatched, Matched
                                            {"label": "Online", "value": "online"},
                                            #Offline: Order completed, expired
                                            {"label": "Offline", "value": "offline"},
                                        ],
                                        value="all",
                                        labelStyle={"display": "inline-block","margin-left":"4px","margin-right":"4px"},
                                        className="dcc_control",
                                    ),
                                    dcc.Dropdown(
                                        id="task_types",
                                        options=task_type_options,
                                        multi=True,
                                        value=[0,1,2],
                                        className="dcc_control",
                                    ),
                                    html.Hr(),
                                    #Pie chart
                                    dcc.Graph(id="task_pie_graph",style={"height": "300px"})
                            ]),
                        ]),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),

                html.Div(
                    [

                        #-------------------------------------------------
                        html.Div(
                            [
                                html.Div(
                                    [html.H4(id="task_num",style={"font-weight":"600","font-size":"1.8em","color":"rgb(96, 96, 96)"}),
                                     html.Small("No. of Tasks"),
                                     #Set the icon, depending on the Font Awesome 5.11.2 CSS file, that is, assets->css->font.css of this project
                                     html.Div(html.I(className="fas fa-list-ol fa-2x",style={"color":"#D7DBDD"}),style={"float": "right","position":"relative","bottom":"40px","right":"20px"})
                                     ],
                                    id="task_text",
                                    className="mini_container",
                                    style={"height":"110px"}
                                ),

                                html.Div(
                                    [html.H4(id="revenue_text",style={"font-weight":"600","font-size":"1.8em","color":"rgb(96, 96, 96)"}), html.Small("Revenue"),
                                     html.Div(html.I(className="fas fa-file-invoice-dollar fa-2x",style={"color":"#D7DBDD"}),
                                              style={"float": "right", "position": "relative", "bottom": "40px",
                                                     "right": "20px"})
                                     ],
                                    id="task_text",
                                    className="mini_container",
                                    style={"height": "110px"}
                                ),
                                html.Div(
                                    [html.H4(html.B(id="matching_rate_text"),style={"font-weight":"600","font-size":"1.8em","color":"rgb(96, 96, 96)"}),
                                     html.Small("Matching Rate"),
                                     html.Div(html.I(className="fas fa-check fa-2x",style={"color":"#CCD1D1"}),
                                              style={"float": "right", "position": "relative", "bottom": "40px",
                                                     "right": "20px"})
                                     ],
                                    id="task_text",
                                    className="mini_container",
                                    style={"height": "110px"}
                                ),
                                html.Div(
                                    [html.H4(id="completion_rate_text",style={"font-weight":"600","font-size":"1.8em","color":"rgb(96, 96, 96)"}),
                                     html.Small("Completion Rate"),
                                     html.Div(html.I(className="fas fa-check-circle fa-2x",style={"color":"#ABB2B9"}),
                                              style={"float": "right", "position": "relative", "bottom": "40px",
                                                     "right": "20px"})
                                     ],
                                    id="task_text",
                                    className="mini_container",
                                    style={"height": "110px"}
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="time_windows_graph",style={"height":"500px"}),
                             ],

                            id="countGraphContainer",
                            className="pretty_container",

                        ),

                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        #Two DIVs on the second line
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="main_task_graph",style={"height":"350px"})],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="worker_graph",style={"height":"350px"}),],
                    className="pretty_container five columns",
                ),
                html.Div(
                    [dcc.Graph(id="worker_pie_graph",style={"height":"350px"})],
                    className="pretty_container five columns",
                ),

            ],
            className="row flex-display",
        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


