from aiohttp import web
import syslog
import aiohttp_jinja2
import aiohttp_debugtoolbar
import jinja2
import subprocess
import mydaemon

button_state = {'checked': '' , '': 'disabled'}
flag_state = {'disable': '' , 'enable': 'checked'}


async def render_page(request):
    context = {'status': request.app['status'],
               'disabled': button_state[request.app['checked']],
               'checked': request.app['checked']}
    return aiohttp_jinja2.render_template('index.html', request,context)

async def handle_command(request):
    command = request.match_info['command']
    syslog.syslog('Have command ' + command)
    if command in ['disable', 'enable']:
        request.app['checked'] = flag_state[command]
    elif command in ['start', 'restart', 'stop']:
        mydaemon.send_command(command)
        request.app['status'] = mydaemon.get_daemon_status()
    raise web.HTTPFound('/')

def init_web(checked):
    app = web.Application(middlewares=[aiohttp_debugtoolbar.middleware], )
    # app = web.Application()

    app['status'] = mydaemon.get_daemon_status()
    app['checked'] = checked

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    app.add_routes([web.get('/', render_page),
                    web.get('/{command}', handle_command)
                    ])
    return app
