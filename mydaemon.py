from aiohttp import web
import syslog
import aiohttp_jinja2
import aiohttp_debugtoolbar
import jinja2
import subprocess

daemon = r'/etc/init.d/cups'

def get_daemon_status():
    prog = subprocess.Popen([daemon, 'status'], stdout=subprocess.PIPE)
    out = str(prog.communicate(timeout=5))
    if 'Active: inactive' in out:
        return 'Сервис остановлен'
    if 'Active: active' in out:
        return 'Сервис работает'
    return 'Статус неопределен'

def send_command(command):
    subprocess.Popen([daemon, command]).communicate(timeout=10)
