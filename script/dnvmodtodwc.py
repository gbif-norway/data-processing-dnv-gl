import pandas as pd
import uuid
from pyproj import Proj, transform

def get_event_and_occurrence(pivot_data, stations_report, current_sea): # Wrapper for other methods
    occurrence = reverse_occurrence_pivot(pivot_data)
    add_uuids(occurrence)
    set_taxonomy_data(occurrence)
    event = create_event_sheet(occurrence, stations_report)
    set_location_data(event, current_sea)
    return event, occurrence

def reverse_occurrence_pivot(pivot_data): # Changes data to 1 record per row, not a grid
    occurrence = pd.melt(pivot_data, id_vars=('Species', 'Family'), var_name='Station', value_name='individualCount')
    occurrence.dropna(inplace=True, subset=['individualCount'])
    occurrence['individualCount'] = occurrence['individualCount'].astype(int)
    return occurrence

def add_uuids(occurrence):
    occurrence['occurrenceID'] = [uuid.uuid4() for x in range(len(occurrence.index))]
    occurrence['eventID'] = occurrence.groupby('Station')['Station'].transform(lambda x: uuid.uuid4())

def set_taxonomy_data(occurrence):
    occurrence['basisOfRecord'] = 'MaterialSample'
    occurrence.rename(columns={'Species': 'scientificName', 'Family': 'family'}, inplace=True)
    occurrence['class'] = ''
    occurrence.loc[occurrence['scientificName'] == 'Oligochaeta', 'class'] = 'Clitellata'
    occurrence.loc[occurrence['scientificName'] == 'Grania', 'family'] = 'Enchytraeidae'

def create_event_sheet(occurrence, stations_report):
    station_years = occurrence['Station'].str.split(' ', expand=True)
    event = pd.DataFrame({
        'eventID': occurrence['eventID'],
        'Station': station_years[1],
        'eventRemarks': 'grab ' + station_years[2],
        'year': station_years[0],
        'eventDate': station_years[0] + '-05/' + station_years[0] + '-06'
    })
    event.drop_duplicates(inplace=True)
    event = pd.merge(event, stations_report, how='left', on='Station')
    return event

def set_location_data(event, current_sea):
    event['waterBody'] = current_sea
    event['geodeticDatum'] = 'WGS84'
    event['locationRemarks'] = 'station ' + event['Station'] + ', direction from station: ' + event['Direction'].astype(str) + ', distance from station: ' + event['Distance'].astype(str)
    event['locationRemarks'] = event['locationRemarks'].str.replace(', direction from station: nan, distance from station: nan', '')
    event['locationRemarks'] = event['locationRemarks'].str.replace(', direction from station: None, distance from station: None', '')
    event['maximumDepthInMeters'] = event['Depth']
    event.drop(columns=['Distance', 'Direction', 'UTM31E', 'UTM31N', 'UTM32E', 'UTM32N', 'UTM34E', 'UTM34N', 'UTM35E', 'UTM35N', 'UTM36E', 'UTM36N', 'ED50E', 'ED50N'], inplace=True)

    event['verbatimCoordinateSystem'] = 'UTM'
    event['verbatimSrS'] = 'EPSG:32633'
    event.rename(columns={'Installation': 'locality', 'Depth': 'minimumDepthInMeters', 'WGS84E': 'decimalLongitude', 'WGS84N': 'decimalLatitude', 'UTM33E': 'verbatimLongitude', 'UTM33N': 'verbatimLatitude'}, inplace=True)
    convert_utm_coordinates(event)

def convert_utm_coordinates(event):
    utm_records = pd.isnull(event['decimalLatitude'])
    if not len(event[utm_records]):
        return
    #inProj, outProj = Proj('epsg:32633'), Proj('epsg:4326')
    inProj, outProj = Proj(proj='utm', zone=33, ellps='WGS84'), Proj('epsg:4326')
    verbatim_lat = event.loc[utm_records, 'verbatimLatitude']
    verbatim_long = event.loc[utm_records, 'verbatimLongitude']
    event.loc[utm_records, 'geodeticDatum'] = 'EPSG:32633'
    event.loc[utm_records, 'decimalLatitude'], event.loc[utm_records, 'decimalLongitude'] = transform(inProj, outProj, verbatim_long.tolist(), verbatim_lat.tolist())
    #event.loc[utm_records, 'decimalLongitude'] = event.loc[utm_records, 'decimalLongitude'].transform(lambda x: round(x, 5))
    #event.loc[utm_records, 'decimalLatitude'] = event.loc[utm_records, 'decimalLatitude'].transform(lambda x: round(x, 5))

