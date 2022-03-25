from dash import dcc,html
from dash.dependencies import Input, Output
import feffery_antd_components as fac

from server import app

from views.simulator import simulator_page
from views.DRL import DRL_page

app.layout = html.Div(
    [
        # layout
        fac.AntdLayout(
            [
                fac.AntdHeader(
                    fac.AntdTitle(
                        # 'AMSAS:  A Visual Analysis System for Spatial Crowdsourcing',
                        'AMSAS',
                        level=2,
                        style={
                            'fontFamily':"Times New Roman",
                            'color': 'white',
                            'margin': '0'
                        }
                    ),
                    style={
                        'display': 'flex',
                        'justifyContent': 'left',
                        'alignItems': 'center'
                    },

                ),
                fac.AntdLayout(
                    [
                        fac.AntdSider(
                            [
                            html.Div(
                                fac.AntdInput(placeholder='Search...', mode='search',id='search'),
                                style={
                                    'padding': '5px'
                                }
                            ),
                            html.Div(
                                fac.AntdMenu(
                                    id='menus',
                                    menuItems=[
                                        {
                                            'component': 'Item',
                                            'props': {
                                                'key': 'simulator',
                                                'title': 'ANALYSIS',
                                                # 'icon': 'line-chart'
                                                'icon':'fc-area-chart'
                                            }
                                        }, {
                                            'component': 'Item',
                                            'props': {
                                                'key': 'DRL',
                                                'title': 'DRL',
                                                'icon': 'fc-mind-map'
                                            }
                                        },

                                    ],
                                    mode='inline'
                                    # renderCollapsedButton=True
                                ),

                                style={
                                    'alignItems': 'left',
                                    'display': 'flex',
                                    'backgroundColor': '#fafafa',
                                    'height': '100%',
                                    'overflowY': 'auto'
                                }
                            ),
                            ],

                            collapsible=True,
                            style={
                                'backgroundColor': 'rgb(240, 242, 245)',
                                'display': 'flex',
                                'justifyContent': 'center'

                            }
                        ),
                        fac.AntdLayout(
                            [
                                fac.AntdContent(
                                    html.Div(
                                        id='page-content',
                                        style={
                                            'height': '100%',
                                            'justifyContent': 'center',
                                            'alignItems': 'center'
                                        },

                                    ),
                                    style={
                                        'backgroundColor': 'white'
                                    },

                                ),
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# Routing master control, integrated search function
@app.callback(
    Output('page-content', 'children'),
    [Input('menus', 'currentKey'),
     Input('search', 'value')
     ]
)
def render_page_content(currentKey,val):

    if val == 'simulator':
        return simulator_page

    elif val == 'DRL':
        return DRL_page

    elif currentKey == 'simulator':
        return simulator_page

    elif currentKey == 'DRL':
        return DRL_page

    elif val == 'simulator':
        return simulator_page

    elif val == 'DRL':
        return DRL_page

    return simulator_page


if __name__ == '__main__':
    app.run_server(debug=True)
