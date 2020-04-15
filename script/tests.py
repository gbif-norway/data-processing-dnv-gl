import unittest
from dnvmodtodwc import reverse_occurrence_pivot, add_uuids, create_event_sheet, dwcify_columns
import pandas as pd
import numpy as np
import uuid

class TestDNVGLMODToDwC(unittest.TestCase):
    def test_create_event_sheet(self):
        occurrence = pd.DataFrame({'Station': ['2008 R10-1 1', '2008 R10-1 1', '2008 R10-1 2', '2010 NV9 5'],
                                   'eventID': [10, 10, 11, 12],
                                   'Species': ['A', 'B', 'A', 'A']})
        stations_report = pd.DataFrame({'Station': ['R10-1', 'NV9'],
                                        'decimalLatitude': [70, 80],
                                        'decimalLongitude': [20, 30]})
        events = create_event_sheet(occurrence, stations_report)
        expected = pd.DataFrame({'eventID': [10, 11, 12],
                                 'Station': ['R10-1', 'R10-1', 'NV9'],
                                 'eventRemarks': ['grab 1', 'grab 2', 'grab 5'],
                                 'year': ['2008', '2008', '2010'],
                                 'month': ['4', '4', '4'],
                                 'decimalLatitude': [70, 70, 80],
                                 'decimalLongitude': [20, 20, 30]})
        np.testing.assert_array_equal(events.values, expected.values)


class TestReverseOccurrencePivot(unittest.TestCase):
    def test_does_not_create_records_for_null_individual_counts(self):
        test_df = pd.DataFrame({'Species': ['A', 'B', 'C'],
                                'Family': ['D', 'E', 'F'],
                                '2008 R10-1 1': [1, None, 2],
                                '2010 NV9 5': [None, 3, None],
                                '2011 EI12 1': [4, 5, 6]})
        result = reverse_occurrence_pivot(test_df)
        df_cols = {'Species': ['A', 'C', 'B', 'A', 'B', 'C'],
                   'Family': ['D', 'F', 'E', 'D', 'E', 'F'],
                   'Station': ['2008 R10-1 1', '2008 R10-1 1', '2010 NV9 5', '2011 EI12 1', '2011 EI12 1', '2011 EI12 1'],
                   'individualCount': [1, 2, 3, 4, 5, 6]}
        expected_result = pd.DataFrame(df_cols)
        np.testing.assert_array_equal(result.values, expected_result.values)

    def test_does_not_remove_rows_with_null_family(self):
        test_df = pd.DataFrame({'Species': ['A', 'B', 'C'],
                                'Family': [None, None, 'F'],
                                '2008 R10-1 1': [1, None, 2],
                                '2010 NV9 5': [None, 3, None],
                                '2011 EI12 1': [4, 5, 6]})
        result = reverse_occurrence_pivot(test_df)
        df_cols = {'Species': ['A', 'C', 'B', 'A', 'B', 'C'],
                   'Family': [None, 'F', None, None, None, 'F'],
                   'Station': ['2008 R10-1 1', '2008 R10-1 1', '2010 NV9 5', '2011 EI12 1', '2011 EI12 1', '2011 EI12 1'],
                   'individualCount': [1, 2, 3, 4, 5, 6]}
        expected_result = pd.DataFrame(df_cols)
        np.testing.assert_array_equal(result.values, expected_result.values)

class TestAddUUIDs(unittest.TestCase):
    def setUp(self):
        self.result = pd.DataFrame({'Station': ['2008 R10-1 1', '2008 R10-1 1', '2010 NV9 5', '2011 EI12 1'],
                                    'Species': ['A', 'B', 'A', 'A']})
        add_uuids(self.result)

    def test_creates_occurrenceID_column(self):
        self.assertTrue('occurrenceID' in self.result.columns)

    def test_creates_uuids_in_occurrenceID_column(self):
        self.assertTrue(isinstance(self.result['occurrenceID'][0], uuid.UUID))
        self.assertTrue(isinstance(self.result['occurrenceID'][1], uuid.UUID))

    def test_creates_unique_uuids_in_occurrenceID_column(self):
        self.assertEqual(len(set(self.result['occurrenceID'].values)), len(self.result))

    def creates_eventID_column(self):
        self.assertTrue('eventID' in self.result.columns)

    def creates_uuids_in_eventID_column(self):
        self.assertTrue(isinstance(self.result['eventID'][0], uuid.UUID))
        self.assertTrue(isinstance(self.result['eventID'][1], uuid.UUID))

    def uses_same_uuid_for_same_events(self):
        self.assertEqual(self.result['eventID'][0], self.result['eventID'][1])

    def has_different_uuids_for_different_events(self):
        self.assertNotEqual(self.result['eventID'][0], self.result['eventID'[2]])
        self.assertNotEqual(self.result['eventID'][0], self.result['eventID'[2]])
        self.assertEqual(len(self.result['eventID'].values) - 1, len(set(self.result['eventID'].values)))

if __name__ == '__main__':
    unittest.main()
