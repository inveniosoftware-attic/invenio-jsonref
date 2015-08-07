# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test JsonRef API."""

import urlparse

from mock import patch
from collections import namedtuple
from flask import current_app

from invenio.testsuite import InvenioTestCase


class TestRecordDereference(InvenioTestCase):
    """Record - testing getting record with external references"""
    
    def test_records_dereference(self):
        """Record - Getting record with remote references"""
        with patch('invenio_records.api.RecordMetadata') as mock_metadata:
            from invenio_records.api import get_record
            record_tuple = namedtuple('RecordTuple', ['json'])

            url_prefix = current_app.config['CFG_SITE_URL']

            fake_records = {
                1: record_tuple({"param1": {"$ref": urlparse.urljoin(url_prefix, "record/2")},
                                 "param2": {"$ref": urlparse.urljoin(url_prefix, "record/3")}}),
                2: record_tuple({"param3": "test_param_3"}),
                3: record_tuple({"param4": "test_param_4"}),
                4: record_tuple({
                    "param_top": {
                        "param_bottom": {"$ref": urlparse.urljoin(url_prefix, "record/3")}
                    }
                }),
                5: record_tuple({
                    "param5": [
                        {"$ref": urlparse.urljoin(url_prefix, "record/3")}
                    ]
                })
            }

            mock_metadata.query = fake_records
            record = get_record(1)

            assert record['param1'] == fake_records[2].json
            assert record['param2'] == fake_records[3].json

            record = get_record(2)
            assert record['param3'] == "test_param_3"

            record = get_record(3)
            assert record['param4'] == "test_param_4"

            record = get_record(4)
            assert record['param_top']['param_bottom']['param4'] == "test_param_4"

            record = get_record(5)
            assert record['param5'][0]['param4'] == "test_param_4"

