import pandas as pd
import uuid

def reverse_occurrence_pivot(pivot_data): # Changes data to 1 record per row, not a grid
    occurrence = pd.melt(pivot_data, id_vars=('Species', 'Family'), var_name='Station', value_name='individualCount')
    occurrence.dropna(inplace=True, subset=['individualCount'])
    occurrence['individualCount'] = occurrence['individualCount'].astype(int)
    return occurrence

def add_uuids(occurrence):
    occurrence['occurrenceID'] = [uuid.uuid4() for x in range(len(occurrence.index))]
    occurrence['eventID'] = occurrence.groupby('Station')['Station'].transform(lambda x: uuid.uuid4())

def create_event_sheet(occurrence, stations_report, current_sea):
    station_years = occurrence['Station'].str.split(' ', expand=True)
    event = pd.DataFrame({
        'eventID': occurrence['eventID'],
        'Station': station_years[1],
        'eventRemarks': 'grab ' + station_years[2],
        'year': station_years[0],
        'month': '4',
        'geodeticDatum': 'WGS84',
        'waterBody': current_sea
    })
    event.drop_duplicates(inplace=True)
    event['eventDate'] = event['year'].apply(lambda x: '{}-05/{}-06'.format(x, x))
    return pd.merge(event, stations_report, how='left', on='Station')

def dwcify_columns(occurrence, event):
    occurrence['basisOfRecord'] = 'MaterialSample'
    occurrence.rename(columns={'Species': 'scientificName', 'Family': 'family'}, inplace=True)
    #occurrence.drop(columns='Station', inplace=True)
    event['locationRemarks'] = 'station ' + event['Station'] + ', direction from station: ' + event['Direction'].astype(str) + ', distance from station: ' + event['Distance'].astype(str)
    #event.drop(columns=['Station', 'Direction', 'Distance'], inplace=True)
    event['maximumDepthInMeters'] = event['Depth']
    event.rename(columns={'Installation': 'locality', 'Depth': 'minimumDepthInMeters', 'WGS84E': 'decimalLongitude', 'WGS84N': 'decimalLatitude'}, inplace=True)

