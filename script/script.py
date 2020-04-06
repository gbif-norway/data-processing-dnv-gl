import pandas as pd
import uuid

stations_cols = ['Installation', 'Station', 'Direction', 'Distance', 'Depth', 'WGS84E', 'WGS84N']
stations_report = pd.ExcelFile('barentshavet_sor_x_stations.xlsx').parse('Stations_Report.xlsx', usecols=stations_cols)
pivot_data = pd.ExcelFile('barentshavet_sor_x.xlsx').parse('Biology_Report.xlsx')

# def reverse_occurrence_pivot(pivot_data): # Changes data to 1 record per row, not a grid
occurrence = pd.melt(pivot_data, id_vars=('Species', 'Family'), var_name='Station', value_name='individualCount')
occurrence.dropna(inplace=True)

# def add_uuids(occurrence):
occurrence['occurrenceID'] = [uuid.uuid4() for x in range(len(occurrence.index))]
occurrence['eventID'] = occurrence.groupby('Station')['Station'].transform(lambda x: uuid.uuid4())

# def create_event_sheet(occurrence, stations_report):
station_years = occurrence['Station'].str.split(' ', expand=True)
event = pd.DataFrame({
    'eventID': occurrence['eventID'],
    'Station': station_years[1],
    'eventRemarks': 'grab ' + station_years[2],
    'year': station_years[0],
    'month': '4'
})
event.drop_duplicates(inplace=True)
event = pd.merge(event, stations_report, how='left', on='Station')

# def dwcify_columns(occurrence, event):
occurrence.rename(columns={'Species': 'scientificName', 'Family': 'family'}, inplace=True)
occurrence.drop(columns='Station', inplace=True)
event['locationRemarks'] = 'station ' + event['Station'] + ', direction from station: ' + event['Direction'].astype(str) + ', distance from station: ' + event['Distance'].astype(str)
event.drop(columns=['Station', 'Direction', 'Distance'], inplace=True)
event['waterBody'] = 'South Barents Sea'
event['maximumDepthInMeters'] = event['Depth']
event.rename(columns={'Installation': 'locality', 'Depth': 'minimumDepthInMeters', 'WGS84E': 'decimalLongitude', 'WGS84N': 'decimalLatitude'}, inplace=True)


import pdb; pdb.set_trace()


