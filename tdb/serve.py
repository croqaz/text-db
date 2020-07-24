from aiohttp import web

# TO BE IMPLEMENTED

app = web.Application()
app.add_routes([
    # web.get('/', handle),
])

if __name__ == '__main__':
    web.run_app(app)
