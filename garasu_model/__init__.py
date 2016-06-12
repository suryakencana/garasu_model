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

from .model.meta.base import Base, get_session_factory, get_engine, get_tm_session


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('cookpyalchemy.models')``.

    """
    settings = config.get_settings()

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)

    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    config.registry['db_session_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'db',
        reify=True
    )