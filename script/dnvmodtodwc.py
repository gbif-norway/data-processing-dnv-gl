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
    return occurrence[occurrence['individualCount'] > 0]

def add_uuids(occurrence):
    occurrence['occurrenceID'] = [uuid.uuid4() for x in range(len(occurrence.index))]
    occurrence['eventID'] = occurrence.groupby('Station')['Station'].transform(lambda x: uuid.uuid4())

def set_taxonomy_data(occurrence):
    occurrence['basisOfRecord'] = 'MaterialSample'
    occurrence.rename(columns={'Species': 'scientificName', 'Family': 'family'}, inplace=True)
    occurrence['phylum'] = ''
    occurrence['class']  = ''
    occurrence['order'] = ''

    overrides_phylum = {'Crustacea': 'Arthropoda', 'Crustacea juv.': 'Arthropoda', 'Graptolithoidea': 'Hemichordata'}
    overrides_class = {'Aplacophora': 'Caudofoveata', 'Cirripedia': 'Hexanauplia', 'Copepoda': 'Hexanauplia', 'Hexacorallia': 'Anthozoa', 'Hirudinea': 'Clitellata', 'Hydroidolina': 'Hydrozoa', 'Lepadomorpha': 'Hexanauplia', 'Oligochaeta': 'Clitellata', 'Oligochaeta juv.': 'Clitellata', 'Tectibranchiata': 'Gastropoda', 'Tellinoidea': 'Cardiida', 'Thoracica': 'Hexanauplia'}
    overrides_order = {'Aeolidioidea': 'Nudibranchia', 'Amphitrite': 'Terebellida', 'Anomura': 'Decapoda', 'Anthuroidea': 'Isopoda', 'Asellota': 'Isopoda', 'Brachyura': 'Decapoda', 'Brachyura juv.': 'Decapoda', 'Caprelloidea': 'Amphipoda', 'Caridea': 'Decapoda', 'Caridea juv.': 'Decapoda', 'Echinidea': 'Camarodonta', 'Echinidea juv.': 'Camarodonta', 'Echiura': 'Echiuroidea', 'Echiurida': 'Echiuroidea', 'Gymnosomata': 'Pteropoda', 'Hyperiidea': 'Amphipoda', 'Pectinoidea': 'Pectinida', 'Pectinoidea juv.': 'Pectinida', 'Terebellomorpha': 'Terebellida', 'Terebellomorpha juv.': 'Terebellida', 'Veneroidea': 'Venerida'}
    overrides_name = {'Amphitrite': 'Amphitrite Müller, 1771', 'Brachyura juv.': 'Brachyura', 'Caridea juv.': 'Caridea', 'Cirripedia': 'Cirripedia Burmeister, 1834', 'Copepoda': 'Copepoda Milne Edwards, 1840', 'Crustacea': 'Crustacea Brünnich, 1772', 'Crustacea juv.': 'Crustacea Brünnich, 1772', 'Cymothoida': 'Cymothoidae', 'Echinidea': 'Echinidea Kroh & Smith, 2010', 'Echinidea juv.': 'Echinidea Kroh & Smith, 2010', 'Echiurida': 'Echiuridae Quatrefages, 1847', 'Eunereis elittoralis': 'Eunereis elitoralis (Eliason, 1962)', 'Graptolithoidea': 'Graptolithoidea Beklemishev, 1951', 'Gymnosomata': 'Gymnosomata Blainville, 1824', 'Hexacorallia': 'Hexacorallia Haeckel, 1896', 'Hirudinea': 'Hirudinea Savigny, 1822', 'Hydroidolina': 'Hydroidolina Collins, 2000', 'Hyperiidea': 'Hyperiidea H. Milne Edwards, 1830', 'Lepadomorpha': 'Lepadomorpha Pilsbry, 1916', 'Opisthobranchia': 'Opisthobranchia', 'Pectinoidea': 'Pectinoidea Rafinesque, 1815', 'Pectinoidea juv.': 'Pectinoidea Rafinesque, 1815', 'Prosobranchia': 'Prosobranchia', 'Prosobranchia juv.': 'Prosobranchia', 'Tellinoidea': 'Tellinoidea Blainville, 1814', 'Terebellomorpha': 'Terebellomorpha Hatschek, 1893', 'Terebellomorpha juv.': 'Terebellomorpha Hatschek, 1893', 'Thoracica': 'Thoracica Darwin, 1854', 'Tunicata': 'Tunicata Lamarck, 1816', 'Veneroidea': 'Veneroidea Rafinesque, 1815'}
    occurrence.loc[occurrence['scientificName'].isin(overrides_phylum.keys()), 'phylum'] = occurrence.loc[occurrence['scientificName'].isin(overrides_phylum.keys()), 'scientificName'].replace(overrides_phylum)
    occurrence.loc[occurrence['scientificName'].isin(overrides_class.keys()), 'class'] = occurrence.loc[occurrence['scientificName'].isin(overrides_class.keys()), 'scientificName'].replace(overrides_class)
    occurrence.loc[occurrence['scientificName'].isin(overrides_order.keys()), 'order'] = occurrence.loc[occurrence['scientificName'].isin(overrides_order.keys()), 'scientificName'].replace(overrides_order)
    occurrence.loc[occurrence['scientificName'].isin(overrides_name.keys()), 'scientificName'] = occurrence.loc[occurrence['scientificName'].isin(overrides_name.keys()), 'scientificName'].replace(overrides_name)
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

