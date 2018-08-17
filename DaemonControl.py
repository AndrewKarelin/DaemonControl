from aiohttp import web
import syslog
import aiohttp_jinja2
import aiohttp_debugtoolbar
import jinja2
import subprocess

async def render_page(request):
    return aiohttp_jinja2.render_template('index.html', request,
                                          {'status': request.app['status'], 'disabled': request.app['disabled'],
                                           'checked': request.app['checked']})

async def handle_command(request):
    command = request.match_info['command']
    syslog.syslog('have command ' + command)
    if command in ['disable', 'enable']:
        request.app['checked'], request.app['disabled'] = newstate[command]
        with open(flag_state, 'w') as f:
            f.write(command)
    elif command in ['start', 'restart', 'stop']:
        subprocess.Popen([daemon, command]).communicate(timeout=10)
        app['status'] = get_daemon_status(daemon)
    raise web.HTTPFound('/')



def get_daemon_status(name):
    prog = subprocess.Popen([name,'status'],stdout=subprocess.PIPE)
    out = str(prog.communicate(timeout=5))
    if 'Active: inactive' in out:
        return 'Сервис остановлен'
    if 'Active: active' in out:
        return 'Сервис работает'
    return 'Статус неопределен'



newstate = {'disable': ('', 'disabled'), 'enable': ('checked', '')}
flag_state = 'flag.state'
daemon = r'/etc/init.d/cups'

def main():

    syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
    syslog.syslog('Web server controlling daemon starting...')

    app = web.Application(middlewares=[aiohttp_debugtoolbar.middleware], )
    # app = web.Application()
    try:
        with open(flag_state, 'r') as f:
            command = f.readline();
    finally:
        if command not in ['disable', 'enable']:
            command = 'enable'
        app['checked'], app['disabled'] = newstate[command]


    app['status'] = get_daemon_status(daemon)

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    app.add_routes([web.get('/', render_page),
                    web.get('/{command}', handle_command)
                    ])

    web.run_app(app, host='localhost', port=8080)
    syslog.syslog('Web server controlling daemon finish')

if __name__ == '__main__':
    main()