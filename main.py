from aiohttp import web
import syslog
import aiohttp_jinja2
import aiohttp_debugtoolbar
import jinja2
import subprocess
import json
import os.path
import subprocess
import time
import threading


import myweb
import mydaemon

app_config = {}

def load_config():
    global app_config
    def_config = {'flag_state': 'checked', 'host_name': 'localhost', 'port': 8080, 'daemon_name': r'/etc/init.d/cups','poll_interval':60}

    config_file_name = os.path.dirname(__file__) + '/config.json'
    try:
        with open(config_file_name, 'r') as f:
            app_config = json.load(f);
    except:
        app_config = def_config

def save_config():
    config_file_name = os.path.dirname(__file__) + '/config.json'
    try:
        with open(config_file_name, 'w') as f:
            json.dump(app_config,f)
    except: pass

def timer_proc(app):
    while True:
        time.sleep(app_config['poll_interval'])
        status = mydaemon.get_daemon_status()
        if app['status'] != status:
            app['status'] != status
            myweb.render_page()




def main():
    syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
    syslog.syslog('Web server managing ' + mydaemon.daemon + ' starting.')

    load_config()

    app = myweb.init_web(app_config['flag_state'])

    web.run_app(app, host=app_config['host_name'], port=app_config['port'])

    syslog.syslog('Web server managing ' + mydaemon.daemon + ' exiting.')

    app_config['flag_state'] = app['checked']
    save_config()

if __name__ == '__main__':
    if os.geteuid() == 0:
        main()
    else:
        current_script = os.path.realpath(__file__)
        subprocess.call(['sudo','-S', 'python3.6', current_script])

