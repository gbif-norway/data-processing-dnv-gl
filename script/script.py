from dnvmodtodwc import reverse_occurrence_pivot, add_uuids, create_event_sheet, dwcify_columns
import pandas as pd

STATIONS_COLS = ['Installation', 'Station', 'Direction', 'Distance', 'Depth', 'WGS84E', 'WGS84N']
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

