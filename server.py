import dash

app = dash.Dash(
    __name__,
    external_scripts=[''],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# set page title
app.title = 'AMSAS'

server = app.server