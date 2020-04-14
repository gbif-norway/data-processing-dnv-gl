import pandas as pd
import uuid

STATIONS_COLS = ['Installation', 'Station', 'Direction', 'Distance', 'Depth', 'WGS84E', 'WGS84N']

def reverse_occurrence_pivot(pivot_data): # Changes data to 1 record per row, not a grid
    occurrence = pd.melt(pivot_data, id_vars=('Species', 'Family'), var_name='Station', value_name='individualCount')
    occurrence.dropna(inplace=True)
    occurrence['individualCount'] = occurrence['individualCount'].astype(int)
    return occurrence

def add_uuids(occurrence):
    occurrence['occurrenceID'] = [uuid.uuid4() for x in range(len(occurrence.index))]
    occurrence['eventID'] = occurrence.groupby('Station')['Station'].transform(lambda x: uuid.uuid4())

def create_event_sheet(occurrence, stations_report):
    station_years = occurrence['Station'].str.split(' ', expand=True)
    event = pd.DataFrame({
        'eventID': occurrence['eventID'],
        'Station': station_years[1],
        'eventRemarks': 'grab ' + station_years[2],
        'year': station_years[0],
        'month': '4'
    })
    event.drop_duplicates(inplace=True)
    return pd.merge(event, stations_report, how='left', on='Station')

def dwcify_columns(occurrence, event):
    occurrence['basisOfRecord'] = 'MaterialSample'
    occurrence.rename(columns={'Species': 'scientificName', 'Family': 'family'}, inplace=True)
    occurrence.drop(columns='Station', inplace=True)
    event['locationRemarks'] = 'station ' + event['Station'] + ', direction from station: ' + event['Direction'].astype(str) + ', distance from station: ' + event['Distance'].astype(str)
    event.drop(columns=['Station', 'Direction', 'Distance'], inplace=True)
    event['waterBody'] = 'South Barents Sea'
    event['maximumDepthInMeters'] = event['Depth']
    event.rename(columns={'Installation': 'locality', 'Depth': 'minimumDepthInMeters', 'WGS84E': 'decimalLongitude', 'WGS84N': 'decimalLatitude'}, inplace=True)

seas = ['barents_sea_south', 'uk_shelf', 'ekofisk_area', 'finnmark', 'more', 'nordland_area', 'oseberg_area', 'sleipner_area', 'statfjord', 'trondelag_area']
occurrence_dfs = []
event_dfs = []
for current_sea in seas:
    stations_report = pd.ExcelFile('source_files/' + current_sea + '_stations.xlsx').parse('Stations_Report.xlsx', usecols=STATIONS_COLS)
    pivot_data = pd.ExcelFile('source_files/' + current_sea + '.xlsx').parse('Biology_Report.xlsx')
    occurrence = reverse_occurrence_pivot(pivot_data)
    add_uuids(occurrence)
    event = create_event_sheet(occurrence, stations_report)
    dwcify_columns(occurrence, event)

    occurrence_dfs.append(occurrence)
    event_dfs.append(event)
    event.to_csv('result_files/' + current_sea + '_event.csv')
    occurrence.to_csv('result_files/' + current_sea + '_occurrence.csv')
import pdb; pdb.set_trace()

