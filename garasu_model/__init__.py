"""
 # Copyright (c) 06 2016 | suryakencana
 # 6/13/16 nanang.ask@kubuskotak.com
 # This program is free software; you can redistribute it and/or
 # modify it under the terms of the GNU General Public License
 # as published by the Free Software Foundation; either version 2
 # of the License, or (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program; if not, write to the Free Software
 # Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 #  __init__.py
"""
from ._version import get_version

from pyramid.settings import asbool
from .model.meta.base import Base, get_session_factory, get_engine, get_tm_session, bind_engine

__all__ = ('__version__',)
__version__ = get_version()


def tm_activate_hook(request):
    if request.path.startswith(("/_debug_toolbar/", "/static/")):
        return False
    return True


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('cookpyalchemy.models')``.

    """
    settings = config.get_settings()
    should_create = asbool(settings.get('garasu_model.should_create_all', False))
    should_drop = asbool(settings.get('garasu_model.should_drop_all', False))

    # Configure the transaction manager to support retrying retryable
    # exceptions. We also register the session factory with the thread-local
    # transaction manager, so that all sessions it creates are registered.
    config.add_settings({
        "tm.attempts": 3,
        "tm.activate_hook": tm_activate_hook,
        "tm.annotate_user": False,
    })
    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)

    config.registry['db_session_factory'] = session_factory

    # make request.db available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'db',
        reify=True
    )

    # Register a deferred action to bind the engine when the configuration is
    # committed. Deferring the action means that this module can be included
    # before model modules without ill effect.
    config.action(None, bind_engine, (engine,), {
        'should_create': should_create,
        'should_drop': should_drop
    }, order=10)

