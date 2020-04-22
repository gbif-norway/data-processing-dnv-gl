from dnvmodtodwc import reverse_occurrence_pivot, add_uuids, create_event_sheet, set_taxonomy_data, set_location_data
import pandas as pd

seas = ['Barents Sea South', 'UK Shelf', 'Ekofisk area', 'Finnmark', 'Møre', 'Nordland area', 'Oseberg area', 'Sleipner area', 'Statfjord', 'Trondelag area']
occurrence_dfs = []
event_dfs = []
for current_sea in seas:
    file_sea_name = current_sea.lower().replace(' ', '_')

    stations_report = pd.ExcelFile('source_files/' + file_sea_name + '_stations.xlsx').parse('Stations_Report.xlsx')
    pivot_data = pd.ExcelFile('source_files/' + file_sea_name + '.xlsx').parse('Biology_Report.xlsx')
    occurrence = reverse_occurrence_pivot(pivot_data)
    add_uuids(occurrence)
    event = create_event_sheet(occurrence, stations_report)
    event = set_location_data(event, current_sea)
    set_taxonomy_data(occurrence)

    occurrence_dfs.append(occurrence)
    event_dfs.append(event)
    event.to_csv('result_files/' + file_sea_name + '_event.csv')
    occurrence.to_csv('result_files/' + file_sea_name + '_occurrence.csv')

import pdb; pdb.set_trace()
