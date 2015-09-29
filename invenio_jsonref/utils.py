# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Define utility functions."""

import urlparse

from collections import Sequence, Mapping

from jsonref import JsonLoader, JsonRef

from werkzeug.exceptions import NotFound

from .registry import json_loaders


def remote_json_route(string, host=None):
    """Register rule on decorated function."""
    def decorator(f):
        if not hasattr(f, '__remote_json_map__'):
            f.__remote_json_map__ = []
        f.__remote_json_map__.append(dict(string=string, host=host))
        return f
    return decorator


class JsonProxy(JsonLoader, object):

    def __init__(self, *args, **kwargs):
        super(JsonProxy, self).__init__(*args, **kwargs)

    def get_remote_json(self, uri, **kwargs):
        splitted_url = urlparse.urlsplit(uri)
        try:
            json_loader, args = json_loaders.bind(splitted_url.hostname).match(splitted_url.path)
            return json_loader(**args)
        except NotFound:
            return super(JsonProxy, self).get_remote_json(uri, **kwargs)

    def create_references(self, data_structure):
        if isinstance(data_structure, (Mapping, Sequence)):
            referenced_data_structure = JsonRef.replace_refs(data_structure, loader=self)
            return referenced_data_structure
        return data_structure
