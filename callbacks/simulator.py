import copy
import math
import pathlib
import pandas as pd
import datetime as dt
from dash import dcc,html
from dash.dependencies import Input, Output, State, ClientsideFunction

from server import app

#---------------------------data loading------------------------------
# get relative data folder
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

#Get order status controller
task_type_options=[
    {"label":"New","value":0},
    {"label":"Matched","value":1},
    {"label":"Completed","value":2},
    #New->Expired
    {"label":"Expired I","value":-1},
    #Matched->Expired
    {"label":"Expired II","value":-2},
]

#Load task data
task_df=pd.read_csv(
    DATA_PATH.joinpath("task_8_12_NY.csv"),
    low_memory=False,
)
#Load worker data
workers_set=[]
for i in range(100):
    file_path="workers_NY/worker_"+str(i)+".csv"
    worker_df=pd.read_csv(
        DATA_PATH.joinpath(file_path),
        low_memory=False,
    )
    workers_set.append(worker_df)

#Load time window data
time_window_df=pd.read_csv(
    DATA_PATH.joinpath("time_windows_NY.csv"),
    low_memory=False,
)

# Create global chart template
mapbox_access_token = "pk.eyJ1Ijoid2lsbGFyZC1zbmF5IiwiYSI6ImNrdjZsejd1YjAwdnQzMnI1bWVvZWhzdHQifQ.Z9z2Hoj6TS_sfouvBKP_OA"

#Diagram layout
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        #ChengDu
        # center=dict(lon=104.06, lat=30.67),
        #New York
        center=dict(lon=-73.93, lat=40.76),
        zoom=10,
    ),
)

#New York time slider scale (timestamp 2016-1-01 8:00:00 to 2016-1-01 12:00:00)
time_marks = {
    1451606400:{"label": "8:00"},
    1451608200:{"label": "8:30"},
    1451610000:{"label": "9:00"},
    1451611800:{"label": "9:30"},
    1451613600:{"label": "10:00"},
    1451615400:{"label": "10:30"},
    1451617200:{"label": "11:00"},
    1451619000:{"label": "11:30"},
    1451620800:{"label": "12:00"},
}


#---------------------------Business logic processing------------------------------
def number_format(num):
    '''
    number formatting
    :param num: 1200
    :return: 1.2K
    '''
    if num == 0:
        return "0"

    magnitude = int(math.log(num, 1000))
    mantissa = str(int(num / (1000 ** magnitude)))
    return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


def filter_dataframe(df, well_statuses, well_types, year_slider):
    dff = df[
        df["Well_Status"].isin(well_statuses)
        & df["Well_Type"].isin(well_types)
        & (df["Date_Well_Completed"] > dt.datetime(year_slider[0], 1, 1))
        & (df["Date_Well_Completed"] < dt.datetime(year_slider[1], 1, 1))
    ]
    return dff

def filter_task_type(task_df,time_slider):
    '''
    Filter tasks into 5 categories (0, 1, 2, -1, -2) according to the time range, such as determining the status of tasks that appear after 9:00 at 10:30
    :param task_df:task set
    :param time_slide:[9:00,10:00],
    :return: df of five tasks
    '''
    #Determine the tasks that appear based on the start and end points of time
    task_ddf=task_df[
        (task_df["appear_time"] >= int(time_slider[0]))
        & (task_df["appear_time"] <= int(time_slider[1]))
    ]

    #Divide these tasks into 5 categories according to the end of time
    #New
    task_0_df=task_ddf[((task_ddf["task_state"]==-2)&(task_ddf["matching_time"]>int(time_slider[1]))
                        |(task_ddf["task_state"]==-1)&(task_ddf["expiration_time"]>int(time_slider[1]))
                        | (task_ddf["task_state"] == 2) & (task_ddf["matching_time"] > int(time_slider[1]))
                        )]
    # matched
    task_1_df = task_ddf[(((task_ddf["task_state"]==-2)&(task_ddf["matching_time"]<int(time_slider[1]))
                        & (task_ddf["task_state"] == -2) & (task_ddf["expiration_time"] > int(time_slider[1])))
                        |( (task_ddf["task_state"] == 2) & (task_ddf["matching_time"] < int(time_slider[1]))
                        & (task_ddf["task_state"] == 2) & (task_ddf["completion_time"] > int(time_slider[1]))
                        ))]
    # completed
    task_2_df = task_ddf[
                         (task_ddf["task_state"] == 2) & (task_ddf["completion_time"] < int(time_slider[1]))
                        ]
    # expired I
    task__1_df = task_ddf[
                         (task_ddf["task_state"] == -1) & (task_ddf["expiration_time"] < int(time_slider[1]))
                        ]
    # expired II
    task__2_df = task_ddf[
                         (task_ddf["task_state"] == -2) & (task_ddf["expiration_time"] < int(time_slider[1]))
                        ]
    return task_0_df,task_1_df,task_2_df,task__1_df,task__2_df


def filter_taskframe(task_df, task_statuses,time_slider):
    '''
    Filter tasks by task status and time range
    :param task_df:
    :param task_statuses:
    :param time_slider:
    :return:
    '''
    task_0_df, task_1_df, task_2_df, task__1_df, task__2_df=filter_task_type(task_df,time_slider)

    task_ddf=pd.DataFrame(columns=["index","appear_time","matching_time","completion_time","expiration_time","longitude","latitude","price","task_state","worker_id"])
    if 0 in task_statuses:
        task_ddf = pd.concat([task_ddf,task_0_df], axis=0, ignore_index=True)
    if 1 in task_statuses:
        task_ddf = pd.concat([task_ddf,task_1_df], axis=0, ignore_index=True)
    if 2 in task_statuses:
        task_ddf = pd.concat([task_ddf,task_2_df], axis=0, ignore_index=True)
    if -1 in task_statuses:
        task_ddf = pd.concat([task_ddf,task__1_df], axis=0, ignore_index=True)
    if -2 in task_statuses:
        task_ddf = pd.concat([task_ddf,task__2_df], axis=0, ignore_index=True)

    return task_ddf

# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("time_windows_graph", "figure")],
)

# Radio -> multi
@app.callback(Output("task_types", "value"), [Input("task_type_selector", "value")])
def display_type(selector):
    if selector == "all":
        return [0,1,2,-1,-2]
    elif selector == "online":
        return [0,1,2]
    elif selector == "offline":
        return [-1,-2]


@app.callback(Output("time_slider", "value"), [Input("time_windows_graph", "selectedData")])
def update_time_slider(time_windows_graph_selected):

    if time_windows_graph_selected is None:
        return [1451610000, 1451615400]

    nums = [int(point["x"]) for point in time_windows_graph_selected["points"]]
    return [min(nums), max(nums)]


# Selectors -> task number,revenue,matching rate, completion rate,task pie
@app.callback(
    [
        Output("task_num", "children"),
        Output("revenue_text", "children"),
        Output("matching_rate_text", "children"),
        Output("completion_rate_text", "children"),
        Output("task_pie_graph", "figure")
     ],
    [
        Input("task_types", "value"),
        Input("time_slider", "value"),
    ],
)
def update_text_pie(task_types, time_slider):

    #data preprocessing
    task_0_df, task_1_df, task_2_df, task__1_df, task__2_df = filter_task_type(task_df, time_slider)
    task_total_num = get_task_num(task_types, task_0_df, task_1_df, task_2_df, task__1_df, task__2_df)

    #update task_number
    dff = filter_taskframe(task_df, task_types, time_slider)

    #update revenue
    if 2 in task_types:
        revenue_df=time_window_df[
        (time_window_df["time_index"] >= int(time_slider[0]))
        & (time_window_df["time_index"] <= int(time_slider[1]))
    ]
        #After selecting the time frame, calculate the total return
        total_revenue=int(revenue_df['revenue'].sum())
    else:
        total_revenue = 0

    #update matching rate
    if task_total_num == 0:
        return str(0) + ' %'
    # Tasks in the matched state
    rate_1 = (task_1_df.shape[0] / task_total_num) * 100
    # task in completed state
    rate_2 = (task_2_df.shape[0] / task_total_num) * 100
    matching_rate = 0

    if 1 in task_types:
        matching_rate += rate_1
    if 2 in task_types:
        matching_rate += rate_2

    # update completion rate
    completion_rate=0
    if task_total_num != 0 and 2 in task_types:
        completion_rate=int((task_2_df.shape[0] / task_total_num) * 100)

    #update task pie
    #Initialize layout
    layout_task_pie = copy.deepcopy(layout)
    # Get processed pie chart data
    data_pie_set = pre_worker_pie(task_df, time_slider, task_types,0)

    # Load Data
    data_pie = [dict(
        type="pie",
        labels=data_pie_set[0],
        values=data_pie_set[1],
        name="Overall Task Summary",
        text=data_pie_set[0],
        hoverinfo="text+value+percent",
        textinfo="label+percent+name",
        hole=0.5,
        marker=dict(colors=data_pie_set[2]),
        # domain={"x": [0, 0.45], "y": [0.2, 0.8]},
    ), ]

    layout_task_pie["title"] = dict(
        text="Overall Task Summary",
        xanchor="auto",
        yanchor="auto"
    )

    figure_pie = dict(data=data_pie, layout=layout_task_pie)

    return dff.shape[0],total_revenue,str(int(matching_rate))+' %',str(completion_rate) + ' %',figure_pie

def get_task_num(task_types, task_0_df, task_1_df, task_2_df, task__1_df, task__2_df):
    '''
    Get the total number of tasks in the specified state during the specified time period
    :param task_types: task type
    :return:
    '''
    task_num=0
    if 0 in task_types:
        task_num+=task_0_df.shape[0]
    if 1 in task_types:
        task_num += task_1_df.shape[0]
    if 2 in task_types:
        task_num += task_2_df.shape[0]
    if -1 in task_types:
        task_num += task__1_df.shape[0]
    if -2 in task_types:
        task_num += task__2_df.shape[0]
    return task_num

@app.callback(
    Output("main_task_graph", "figure"),
    [
        Input("task_types", "value"),
        Input("time_slider", "value"),
    ],
    [State("main_task_graph", "relayoutData")],
)
def make_task_main_figure(
    task_types, time_slider, main_task_graph_layout
):
    '''
    Draw order distribution map
    :param task_types:
    :param time_slider:
    :param main_task_graph_layout:
    :return:
    '''
    task_0_df, task_1_df, task_2_df, task__1_df, task__2_df = filter_task_type(task_df, time_slider)
    traces = []
    if 0 in task_types:
        trace = dict(
            type="scattermapbox",
            lon=task_0_df["longitude"],
            lat=task_0_df["latitude"],
            text=["worker_"+ str(i) for i in task_0_df["worker_id"]],
            customdata=task_0_df["index"],
            name="New",
            #symbol="bug"    #Properties can define their own icons https://www.mapbox.com/maki-icons/
            marker=dict(size=4, opacity=0.6)
        )
        traces.append(trace)
    if 1 in task_types:
        trace = dict(
            type="scattermapbox",
            lon=task_1_df["longitude"],
            lat=task_1_df["latitude"],
            text=["worker_"+ str(i) for i in task_1_df["worker_id"]],
            customdata=task_1_df["index"],
            name="Matched",
            marker=dict(size=4, opacity=0.6),
        )
        traces.append(trace)
    if 2 in task_types:
        trace = dict(
            type="scattermapbox",
            lon=task_2_df["longitude"],
            lat=task_2_df["latitude"],
            text=["worker_"+ str(i) for i in task_2_df["worker_id"]],
            customdata=task_2_df["index"],
            name="Completed",
            marker=dict(size=4, opacity=0.6),
        )
        traces.append(trace)
    if -1 in task_types:
        trace = dict(
            type="scattermapbox",
            lon=task__1_df["longitude"],
            lat=task__1_df["latitude"],
            text=["worker_"+ str(i) for i in task__1_df["worker_id"]],
            customdata=task__1_df["index"],
            name="Expired I",
            marker=dict(size=4, opacity=0.6),
        )
        traces.append(trace)
    if -2 in task_types:
        trace = dict(
            type="scattermapbox",
            lon=task__2_df["longitude"],
            lat=task__2_df["latitude"],
            text=["worker_"+ str(i) for i in task__2_df["worker_id"]],
            customdata=task__2_df["index"],
            name="Expired II",
            marker=dict(size=4, opacity=0.6),
        )
        traces.append(trace)

    # relayoutData is None by default, and {'autosize': True} without relayout action
    if main_task_graph_layout is not None:
        if "mapbox.center" in main_task_graph_layout.keys():
            lon = float(main_task_graph_layout["mapbox.center"]["lon"])
            lat = float(main_task_graph_layout["mapbox.center"]["lat"])
            zoom = float(main_task_graph_layout["mapbox.zoom"])
            layout["mapbox"]["center"]["lon"] = lon
            layout["mapbox"]["center"]["lat"] = lat
            layout["mapbox"]["zoom"] = zoom

    figure = dict(data=traces, layout=layout)
    return figure

def pre_worker_task(task_ddf,time_slider):
    '''
    Calculate the change of the worker's backpack and the change of income every 1 minute as a time slice within the specified time range
    :param task_ddf:
    :param time_slider:
    :return:
    '''
    data=[[],[],[]]
    capacity=0
    revenue=0
    for t in range(time_slider[0],time_slider[1],60):
        start_time=t
        end_time=t+60
        #Statistics of newly added backpack tasks during this period
        add_df = task_ddf[(((task_ddf["task_state"]==2)&(task_ddf["matching_time"]>start_time)&(task_ddf["matching_time"]<end_time)
                            &(task_ddf["completion_time"]>end_time))
                        |((task_ddf["task_state"]==-2)&(task_ddf["matching_time"]>start_time)&(task_ddf["matching_time"]<end_time)
                          &(task_ddf["expiration_time"]>end_time))
                        )]
        capacity+=add_df.shape[0]
        # Statistics of completed and overdue tasks during this period
        reduce_df=task_ddf[(((task_ddf["task_state"]==2)&(task_ddf["completion_time"]>start_time)&(task_ddf["completion_time"]<end_time))
                        |((task_ddf["task_state"]==-2)&(task_ddf["expiration_time"]>start_time)&(task_ddf["expiration_time"]<end_time))
                        )]
        capacity -= reduce_df.shape[0]
        #Total revenue during this period
        revenue_df=task_ddf[((task_ddf["task_state"]==2)&(task_ddf["completion_time"]>start_time)&(task_ddf["completion_time"]<end_time))]
        revenue+=revenue_df['price'].sum()

        #load data
        data[0].append(end_time)
        data[1].append(capacity)
        data[2].append(revenue)

    return data

def pre_worker_pie(worker_task_df, time_slider,task_types,pie_type):
    '''
    Count the number of various task types within a specified time range
    :param worker_task_df: task set
    :param time_slider: time range
    :param task_types: task type
    :param pie_type: graph type，0; include Expired I 1: no include
    :return:
    '''
    data_pie=[[],[],[]]
    task_0_df, task_1_df, task_2_df, task__1_df, task__2_df = filter_task_type(worker_task_df, time_slider)
    # task_total_num = get_task_num(task_types, task_0_df, task_1_df, task_2_df, task__1_df, task__2_df)
    if pie_type==0:
        if -1 in task_types:
            data_pie[0].append('Expired I')
            data_pie[1].append(task__1_df.shape[0])
            data_pie[2].append("#D98880")
        if 0 in task_types:
            data_pie[0].append('New')
            data_pie[1].append(task_0_df.shape[0])
            data_pie[2].append("#7FB3D5 ")


    if 1 in task_types:
        data_pie[0].append('Matched')
        data_pie[1].append(task_1_df.shape[0])
        data_pie[2].append("#FAD7A0")
    if 2 in task_types:
        data_pie[0].append('Completwd')
        data_pie[1].append(task_2_df.shape[0])
        data_pie[2].append( "#7DCEA0")
    if -2 in task_types:
        data_pie[0].append('Expired II')
        data_pie[1].append(task__2_df.shape[0])
        data_pie[2].append("#C39BD3")

    return data_pie

@app.callback(
        [
        Output("worker_graph", "figure"),
        Output("worker_pie_graph", "figure")
        ],
        [
        Input("main_task_graph", "hoverData"),
        Input("task_types", "value"),
        Input("time_slider", "value")
        ])
def make_worker_figure(main_graph_hover,task_types,time_slider):

    layout_worker = copy.deepcopy(layout)
    layout_worker_pie = copy.deepcopy(layout)

    if main_graph_hover is None:
        worker_id=1
    else:
        # Get the worker id to which the mouse hover task belongs
        worker_id=int(str(main_graph_hover["points"][0]["text"]).split('_')[1])
    #Get all tasks of the corresponding worker
    worker_task_df=workers_set[worker_id]
    if worker_id!=-1:

        #Task df after filtering by time and type
        task_dff = filter_taskframe(worker_task_df, task_types, time_slider)
        #Get processed order data
        data_set=pre_worker_task(task_dff,time_slider)
        #Get processed pie chart data
        data_pie_set=pre_worker_pie(worker_task_df, time_slider,task_types,1)
        #load data
        data = [
            dict(
                type="scatter",
                mode="lines",
                name="Capacity",
                x=data_set[0],
                y=data_set[1],
                line=dict(shape="spline", smoothing=1, width=2, color="#a9bb95" ),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines",
                name="Revenue",
                x=data_set[0],
                y=data_set[2],
                yaxis='y2',
                line=dict(shape="spline", smoothing=2, width=2, color="#fac1b7"),
                marker=dict(symbol="diamond-open"),
            ),

        ]
        #pie data
        data_pie = [ dict(
                type="pie",
                labels=data_pie_set[0],
                values=data_pie_set[1],
                name="Worker Task Summary",
                text=data_pie_set[0],
                hoverinfo="text+value+percent",
                textinfo="label+percent+name",
                hole=0.5,
                marker=dict(colors=data_pie_set[2]),
                # domain={"x": [0, 0.45], "y": [0.2, 0.8]},
            ),]

        layout_worker["title"] = "Worker_"+str(worker_id)+" Capacity & Revenue"
        layout_worker_pie["title"] = "Worker_" + str(worker_id) + " Task Summary"
        # Modify the x-axis scale display
        layout_worker["xaxis"] = dict(
            # title="time",
            tickmode='array',
            tickvals=[1451606400,1451608200,1451610000,1451611800,1451613600,1451615400, 1451617200,1451619000,1451620800],
            ticktext=["8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30", "12:00"],
            range=[time_slider[0]-200, time_slider[1]+200]
        )
        layout_worker['yaxis'] = dict(
            side='right',
            color='#117A65'
        )
        #set the second y coordinate
        layout_worker['yaxis2']=dict(
            overlaying='y',
            side='left',
            color = '#AF601A'
        )
    else:
        #The worker id is -1, indicating that this task does not assign the specified worker
        data=None
        data_pie=None

    figure = dict(data=data, layout=layout_worker)
    #pie graph
    figure_pie=dict(data=data_pie, layout=layout_worker_pie)
    return figure,figure_pie

@app.callback(
    Output("time_windows_graph", "figure"),
    Input("time_slider", "value"),
)
def make_time_windows_figure(time_slider):

    layout_count = copy.deepcopy(layout)
    g = time_window_df

    #Histogram Color
    colors = []
    #Scatter Plot Colors
    colors1=[]

    for i in range(g.shape[0]):
        if int(g["time_index"][i]) >= int(time_slider[0]) and int(g["time_index"][i]) < int(time_slider[1]):
            # Blue and purple color
            # colors.append("rgb(123, 199, 255)")
            # colors1.append("rgb(223, 125, 255)")
            #Orange and blue color
            colors.append("rgb(235, 152, 78)")
            colors1.append("rgb(36, 113, 163)")
        else:
            # colors.append("rgba(123, 199, 255, 0.2)")
            # colors1.append("rgba(223, 125, 255,0.2)")
            colors.append("rgba(235, 152, 78 , 0.2)")
            colors1.append("rgba(36, 113, 163 ,0.2)")

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=g["time_index"],
            y=g["window_size"] ,
            name="Size",
            opacity=1,
            # hoverinfo="skip",
            marker=dict(color=colors1),
        ),
        dict(
            type="bar",
            x=g["time_index"],
            y=g["revenue"],
            name="Revenue",
            yaxis='y2',
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "Time Window"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = True
    # layout_count["legend"]=dict(x=10,y=10)
    layout_count["autosize"] = True

    #Modify the x-axis scale display
    layout_count["xaxis"] = dict(
        # title="time",
        tickmode='array',
        tickvals=[1451606400, 1451608200, 1451610000, 1451611800, 1451613600, 1451615400, 1451617200, 1451619000,
                  1451620800],
        ticktext=["8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00"],
        range = [1451606200, 1451621000]
                                 )
    #Modify the y-axis scale display
    layout_count["yaxis"] = dict(
        side='right',
        color='rgb(36, 113, 163)',
        range=[0,29],
    )
    # set the second y coordinate
    layout_count['yaxis2'] = dict(
        overlaying='y',
        side='left',
        color="rgb(235, 152, 78)"
    )

    figure = dict(data=data, layout=layout_count)
    return figure
