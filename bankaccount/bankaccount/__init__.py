from pyramid.config import Configurator
import sqlahelper
from sqlalchemy import engine_from_config
from bankaccount.resources import Root
from pyramid.session import UnencryptedCookieSessionFactoryConfig

my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings)
    sqlahelper.add_engine(engine)
    settings = get_makopath()
    config = Configurator(root_factory=Root,
                          settings=settings,
                          session_factory=my_session_factory)
    config.include('pyramid_tm')
    config.add_route('home', '/')
    config.add_route('deposit', '/deposit')
    config.add_route('withdraw', '/withdraw')
    config.add_static_view('static', 'bankaccount:static')
    config.scan('.views')
    return config.make_wsgi_app()

def get_makopath():
    import os
    here = os.path.dirname(__file__)
    settings = {
            'mako.directories':[
                os.path.abspath(os.path.join(here, 'templates')),
            ],
    }
    return settings