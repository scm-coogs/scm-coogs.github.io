import datetime as dt
import unittest
from unittest.mock import patch

import app


class BuildRequestTests(unittest.TestCase):
    @patch('app.Request')
    @patch('app.Collection')
    @patch('app.BBox')
    def test_builds_spatial_and_temporal_request(self, bbox, collection, request):
        request.return_value.is_valid.return_value = True
        start = dt.date(2024, 1, 2)
        end = dt.date(2024, 1, 3)

        app.build_request(
            ' C123-PROVIDER ',
            '-10',
            '20',
            '10',
            '40',
            start,
            end,
            5,
            ' image/tiff ',
        )

        bbox.assert_called_once_with(-10.0, 20.0, 10.0, 40.0)
        collection.assert_called_once_with(id='C123-PROVIDER')
        request.assert_called_once_with(
            collection=collection.return_value,
            max_results=5,
            spatial=bbox.return_value,
            temporal={
                'start': dt.datetime(2024, 1, 2),
                'stop': dt.datetime(2024, 1, 3, 23, 59, 59, 999999),
            },
            format='image/tiff',
        )

    def test_rejects_partial_bounding_box(self):
        with self.assertRaisesRegex(ValueError, 'all four bounding-box'):
            app.build_request('C123-PROVIDER', west='-10')

    def test_rejects_out_of_range_bounding_box(self):
        with self.assertRaisesRegex(ValueError, 'Use bounds'):
            app.build_request('C123-PROVIDER', '-181', '-10', '10', '10')

    def test_rejects_reversed_dates(self):
        with self.assertRaisesRegex(ValueError, 'start date'):
            app.build_request(
                'C123-PROVIDER',
                start_date=dt.date(2024, 2, 1),
                end_date=dt.date(2024, 1, 1),
            )

    @patch('app.Request')
    @patch('app.Collection')
    def test_allows_request_without_optional_filters(self, collection, request):
        request.return_value.is_valid.return_value = True

        app.build_request('C123-PROVIDER')

        request.assert_called_once_with(
            collection=collection.return_value,
            max_results=10,
        )


if __name__ == '__main__':
    unittest.main()
