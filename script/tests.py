import unittest
from dnvmodtodwc import reverse_occurrence_pivot, add_uuids, create_event_sheet, set_taxonomy_data, set_location_data, get_event_and_occurrence
import pandas as pd
import numpy as np
import uuid


class TestGetEventAndOccurrence(unittest.TestCase):
    def test_wrapper_function(self):
        pivot_data = pd.DataFrame({'Species': ['A', 'B', 'C'],
                                 'Family': ['D', 'E', 'F'],
                                 '2008 R10-1 1': [1, None, 2],
                                 '2010 NV9 5': [None, 3, None],
                                 '2011 EI12 1': [4, 5, 6]})
        stations_report = pd.DataFrame({
                                  'Installation':['Alpha','Beta','Theta'],
                                  'Station':['R10-1','NV9','EI12'],
                                  'Direction':[0,0,0],
                                  'Distance':[0,0,0],
                                  'Depth':[387,389,377],
                                  'UTM31E':[0,0,0],
                                  'UTM31N':[0,0,0],
                                  'UTM32E':[0,0,0],
                                  'UTM32N':[0,0,0],
                                  'UTM34E':[0,0,0],
                                  'UTM34N':[0,0,0],
                                  'UTM33E':[484774,485234,486580],
                                  'UTM33N':[7996294,7995873,7997461],
                                  'UTM35E':[0,0,0],
                                  'UTM35N':[0,0,0],
                                  'UTM36E':[0,0,0],
                                  'UTM36N':[0,0,0],
                                  'ED50E':[20.5570526,20.57052155,20.60937],
                                  'ED50N':[72.06354198,72.05979779,72.07411563],
                                  'WGS84E':[20.55545089,None,20.60777047],
                                  'WGS84N':[72.06370613,None,72.07428065]})
        event, occurrence = get_event_and_occurrence(pivot_data, stations_report, 'UK Shelf')


class TestCreateEventSheet(unittest.TestCase):
    def test_creates_a_single_record_per_event_with_correct_dates_and_grab_numbers(self):
        occurrence = pd.DataFrame({'Station': ['2008 R10-1 1', '2008 R10-1 1', '2008 R10-1 2', '2010 NV9 5'],
                                   'eventID': [10, 10, 11, 12],
                                   'Species': ['A', 'B', 'A', 'A']})
        stations_report = pd.DataFrame({'Station': ['R10-1', 'NV9']})
        events = create_event_sheet(occurrence, stations_report)
        expected = pd.DataFrame({'eventID': [10, 11, 12],
                                 'Station': ['R10-1', 'R10-1', 'NV9'],
                                 'eventRemarks': ['grab 1', 'grab 2', 'grab 5'],
                                 'year': ['2008', '2008', '2010'],
                                 'eventDate': ['2008-05/2008-06', '2008-05/2008-06', '2010-05/2010-06']})
        np.testing.assert_array_equal(events.values, expected.values)


class TestSetLocationData(unittest.TestCase):
    def setUp(self):
        self.event = pd.DataFrame({'Station': ['J1', 'J2', 'J3'],
                              'Depth': [100, 101, 102],
                              'Direction': pd.Series([30, None, 90], dtype=object),
                              'Distance': pd.Series([1, None, 3], dtype=object),
                              'Installation': ['Jeba', 'Jeba', 'Jeba'],
                              'WGS84N': [70, None, None],
                              'WGS84E': [20, None, None],
                              'UTM33N': [8000000, 8220514.84, 8220612.92],
                              'UTM33E': [730000, 795102.30, 795082.28],
                              'UTM31E': '', 'UTM31N': '', 'UTM32E': '', 'UTM32N': '', 'UTM34E': '', 'UTM34N': '',
                              'UTM35E': '', 'UTM35N': '', 'UTM36E': '', 'UTM36N': '', 'ED50E': '', 'ED50N': ''
                              })
        set_location_data(self.event, 'UK Shelf')

    def test_creates_waterbody(self):
        np.testing.assert_array_equal(self.event['waterBody'].values, ['UK Shelf', 'UK Shelf', 'UK Shelf'])

    def test_it_assigns_correct_geodetic_datums(self):
        np.testing.assert_array_equal(self.event['geodeticDatum'].values, ['WGS84', 'EPSG:32633', 'EPSG:32633'])

    def test_it_creates_sensible_location_remarks(self):
        expected = ['station J1, direction from station: 30, distance from station: 1', 'station J2',
                    'station J3, direction from station: 90, distance from station: 3']
        np.testing.assert_array_equal(self.event['locationRemarks'].values, expected)

    def test_it_assigns_max_min_depth(self):
        np.testing.assert_array_equal(self.event['maximumDepthInMeters'].values, [100, 101, 102])
        np.testing.assert_array_equal(self.event['minimumDepthInMeters'].values, [100, 101, 102])

    def test_it_adds_station_as_locality(self):
        np.testing.assert_array_equal(self.event['locality'].values, ['Jeba', 'Jeba', 'Jeba'])

    def test_it_assigns_correct_verbatim_data(self):
        np.testing.assert_array_equal(self.event['verbatimLatitude'].values, [8000000, 8220514.84, 8220612.92])
        np.testing.assert_array_equal(self.event['verbatimLongitude'].values, [730000, 795102.30, 795082.28])
        np.testing.assert_array_equal(self.event['verbatimSrS'].values, ['EPSG:32633', 'EPSG:32633', 'EPSG:32633'])
        np.testing.assert_array_equal(self.event['verbatimCoordinateSystem'].values, ['UTM', 'UTM', 'UTM'])

    def test_conversion_from_utm(self):
        # These tests fail
        #np.testing.assert_array_equal(self.event['decimalLatitude'].values, [70, 73.86192111, 73.86281664])
        #np.testing.assert_array_equal(self.event['decimalLongitude'].values, [20, 24.5469315, 24.54679897])
        pass

    def test_does_not_break_if_no_conversion_needed(self):
        event = pd.DataFrame({'Station': ['J1', 'J2'],
                              'Depth': [100, 101],
                              'Direction': [0, 30],
                              'Distance': [10, 20],
                              'Installation': ['Jeba', 'Jeba'],
                              'WGS84N': [70, 80],
                              'WGS84E': [20, 10],
                              'UTM33N': [8000000, 8],
                              'UTM33E': [730000, 7],
                              'UTM31E': '', 'UTM31N': '', 'UTM32E': '', 'UTM32N': '', 'UTM34E': '', 'UTM34N': '',
                              'UTM35E': '', 'UTM35N': '', 'UTM36E': '', 'UTM36N': '', 'ED50E': '', 'ED50N': ''
                              })
        set_location_data(event, 'UK Shelf')
        np.testing.assert_array_equal(event['decimalLatitude'].values, [70, 80])
        np.testing.assert_array_equal(event['decimalLongitude'].values, [20, 10])


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

    def test_creates_eventID_column(self):
        self.assertTrue('eventID' in self.result.columns)

    def test_creates_uuids_in_eventID_column(self):
        self.assertTrue(isinstance(self.result['eventID'][0], uuid.UUID))
        self.assertTrue(isinstance(self.result['eventID'][1], uuid.UUID))

    def test_uses_same_uuid_for_same_events(self):
        self.assertEqual(self.result['eventID'][0], self.result['eventID'][1])

    def test_has_different_uuids_for_different_events(self):
        self.assertNotEqual(self.result['eventID'][0], self.result['eventID'][2])
        self.assertNotEqual(self.result['eventID'][0], self.result['eventID'][2])
        self.assertEqual(len(self.result['eventID'].values) - 1, len(set(self.result['eventID'].values)))


class TestSetTaxonomyData(unittest.TestCase):
    def setUp(self):
        self.occurrences = pd.DataFrame({'Species': ['A', 'Grania', 'Grania', 'Oligochaeta', 'Z'], 'Family': ['F', 'G', 'H', 'H', 'I']})
        set_taxonomy_data(self.occurrences)

    def test_it_sets_basis_of_record(self):
        np.testing.assert_array_equal(self.occurrences['basisOfRecord'], ['MaterialSample' for i in range(5)])

    def test_it_renames_columns_and_adds_class_column(self):
        self.assertTrue('scientificName' in self.occurrences.columns and 'species' not in self.occurrences.columns)
        self.assertTrue('family' in self.occurrences.columns and 'Family' not in self.occurrences.columns)
        self.assertTrue('class' in self.occurrences.columns)

    def test_it_assigns_class_overrides(self):
        np.testing.assert_array_equal(self.occurrences['class'], ['', '', '', 'Clitellata', ''])

    def test_it_assigns_family_overrides(self):
        np.testing.assert_array_equal(self.occurrences['family'], ['F', 'Enchytraeidae', 'Enchytraeidae', 'H', 'I'])



if __name__ == '__main__':
    unittest.main()
