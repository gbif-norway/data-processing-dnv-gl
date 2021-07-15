from dnvmodtodwc import reverse_occurrence_pivot, add_uuids, create_event_sheet, set_taxonomy_data, set_location_data, get_event_and_occurrence
import pandas as pd

seas = ['Barents Sea South', 'UK Shelf', 'Ekofisk', 'Finnmark', 'More', 'Nordland', 'Oseberg', 'Sleipner', 'Statfjord1', 'Statfjord2', 'Trondelag']
occurrence_dfs = []
event_dfs = []
for current_sea in seas:
    file_sea_name = current_sea.lower().replace(' ', '_')

    stations_report = pd.ExcelFile('source_files/' + file_sea_name + '_stations.xlsx').parse('Stations_Report.xlsx')
    pivot_data = pd.ExcelFile('source_files/' + file_sea_name + '.xlsx').parse('Biology_Report.xlsx')
    event, occurrence = get_event_and_occurrence(pivot_data, stations_report, current_sea)
    occurrence_dfs.append(occurrence)
    event_dfs.append(event)
    #event.to_csv('result_files/' + file_sea_name + '_event.csv')
    #occurrence.to_csv('result_files/' + file_sea_name + '_occurrence.csv')

events = pd.concat(event_dfs)
occurrences = pd.concat(occurrence_dfs)
del occurrences['Station']
all = occurrences.merge(events, how='left', on=['eventID'])

species = pd.read_csv('source_files/species_table.csv', dtype='str')
species = species[species['Source'].isnull()]
del species['ValidationSummary']

latest = all[all['year'] == '2020']
latest = latest.merge(species, how='left', on=['scientificName'])
latest['scientificNameID'] = 'urn:lsid:marinespecies.org:taxname:' + latest['AphiaID']

latest_events = latest[events.columns].drop_duplicates()
latest_occurrences = latest[occurrences.columns.to_list() + ['scientificNameID']]
latest_events.to_csv('result_files/dnv-events-2020.csv', index=False)
latest_occurrences.to_csv('result_files/dnv-occurrences-2020.csv', index=False)

old = pd.read_csv('source_files/old-occurrence.txt', dtype='str', delimiter='\t')
old = old.merge(species, how='left', on=['scientificName'])
old[old['AphiaID'].isnull()]['scientificName'].drop_duplicates()
old['scientificNameID'] = 'urn:lsid:marinespecies.org:taxname:' + old['AphiaID']
old.to_csv('result_files/dnv-occurrences-updatedwithaphia.txt', index=False, sep='\t')

#events.to_csv('result_files/dnv-events.csv', index=False)
#occurrences.to_csv('result_files/dnv-occurrences.csv', index=False)
import pdb; pdb.set_trace()
