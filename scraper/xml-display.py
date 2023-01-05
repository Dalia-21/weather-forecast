from pprint import pprint
from bs4 import BeautifulSoup
import os


current_path = os.path.dirname(__file__)
path_to_files = os.path.join(current_path, "../weather-data/")
files = sorted([os.path.join(path_to_files, file) for file in os.listdir(path_to_files)])
xml_dict = dict()
xml_dict['titles'] = []

for i in range(8):
    # Files have up to 8 index entries
    index_name = 'index_' + str(i)
    xml_dict[index_name] = []

for i in range(8):
    # range is just to keep entries on screen, can be removed later
    with open(files[i], "r") as f:
        data = BeautifulSoup(f, "xml")

    file_name = files[i].split('/')[-1]
    title = file_name[file_name.index('.')+1:]
    xml_dict['titles'].append(title)

    for period in data.area.find_all('forecast-period'):
        index_name = 'index_' + period.attrs['index']

        xml_dict[index_name].append(period.attrs['start-time-local'][:10])


print("Titles: ", xml_dict['titles'])
for i in range(8):
    index_name = 'index_' + str(i)
    print(index_name, xml_dict[index_name])