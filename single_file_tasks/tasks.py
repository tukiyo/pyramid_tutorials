import os
import logging
import sqlite3

from pyramid.config import Configurator

from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import view_config
from pyramid.response import Response

from wsgiref.simple_server import make_server


logging.basicConfig()
log = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

@view_config(context=Exception, renderer='exception.mako')
def error_view(exc, request):
    return {'message':exc}

# views
@view_config(route_name='list', renderer='list.mako')
def list_view(request):
    rs = request.db.execute("select id, name from tasks where closed = 0")
    tasks = [dict(id=row["id"], name=row["name"]) for row in rs.fetchall()]
    return {'tasks': tasks}

@view_config(route_name='closed', renderer='closed.mako')
def closed_list_view(request):
    rs = request.db.execute("select id, name from tasks where closed = 1")
    tasks = [dict(id=row["id"], name=row["name"]) for row in rs.fetchall()]
    return {'tasks': tasks}

@view_config(route_name='reopen')
def reopen_view(request):
    task_id = int(request.matchdict['id'])
    request.db.execute("update tasks set closed = ? where id = ?",
                       (0, task_id))
    request.db.commit()
    request.session.flash('Task was successfully reopen!')
    return HTTPFound(location=request.route_url('list'))

@view_config(route_name='new', renderer='new.mako')
def new_view(request):
    if request.method == 'POST':
        if request.POST.get('name'):
            request.db.execute(
                'insert into tasks (name, closed) values (?, ?)',
                [request.POST['name'], 0])
            request.db.commit()
            request.session.flash('New task was successfully added!')
            return HTTPFound(location=request.route_url('list'))
        else:
            request.session.flash('Please enter a name for the task!')
    return {}


@view_config(route_name='close')
def close_view(request):
    task_id = int(request.matchdict['id'])
    request.db.execute("update tasks set closed = ? where id = ?",
                       (1, task_id))
    request.db.commit()
    request.session.flash('Task was successfully closed!')
    return HTTPFound(location=request.route_url('list'))


@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(request):
    request.response.status = '404 Not Found'
    return {}

# subscribers
@subscriber(NewRequest)
def new_request_subscriber(event):
    request = event.request
    settings = request.registry.settings
    request.db = sqlite3.connect(settings['db'])
    request.db.row_factory = sqlite3.Row
    request.add_finished_callback(close_db_connection)

def close_db_connection(request):
    request.db.close()


@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    log.warn('Initializing database...')
    with open(os.path.join(here, 'schema.sql')) as f:
        stmt = f.read()
        settings = event.app.registry.settings
        db = sqlite3.connect(settings['db'])
        db.executescript(stmt)
        db.commit()


if __name__ == '__main__':
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here, 'templates')
    settings['db'] = os.path.join(here, 'tasks.db')
    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    # configuration setup
    config = Configurator(settings=settings, session_factory=session_factory)
    # routes setup
    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('close', '/close/{id}')
    config.add_route('closed', '/closed')
    config.add_route('reopen', '/reopen/{id}')
    # static view setup
    config.add_static_view('static', os.path.join(here, 'static'))
    # scan for @view_config and @subscriber decorators
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
