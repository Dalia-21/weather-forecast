"""Temporary utility for visualising the data contained
in the weather files."""
from xml_tools import get_files, get_xml
from datetime import datetime
import plotly.graph_objects as go


class WeatherEntry:
    def __init__(self, entry_date):
        self.date = entry_date
        self.indexes = dict()
        self.deltas = dict()
        self.highest_index = 0
        self.lowest_index = 7

    def add_index(self, xml_data):
        index = str(xml_data.attrs['index'])
        if int(index) > self.highest_index:
            self.highest_index = int(index)
        if int(index) < self.lowest_index:
            self.lowest_index = int(index)

        if index in self.indexes or not xml_data:
            return
        else:
            self.indexes[index] = dict()

            try:
                min_temp = int(xml_data.find('element', type="air_temperature_minimum").string)
            except AttributeError:
                min_temp = None
            try:
                max_temp = int(xml_data.find('element', type="air_temperature_maximum").string)
            except AttributeError:
                max_temp = None
            try:
                rainfall = float(xml_data.find('element', type="precipitation_range").string.split()[2])
            except AttributeError:
                rainfall = None
            try:
                chance_of_rain = int(xml_data.find('element', type="probability_of_precipitation").string[:-1])
            except AttributeError:
                chance_of_rain = None

            self.indexes[index]['min_temp'] = min_temp
            self.indexes[index]['max_temp'] = max_temp
            self.indexes[index]['rainfall'] = rainfall
            self.indexes[index]['chance_of_rain'] = chance_of_rain

    def generate_deltas(self):
        """Indexes vary depending on BOM API contents"""
        lowest_index = min(list(map(int, self.indexes.keys())))
        highest_index = max(list(map(int, self.indexes.keys())))

        self.deltas['max_temp'] = self.indexes[lowest_index]['max_temp'] - self.indexes[highest_index]['max_temp']
        self.deltas['min_temp'] = self.indexes[lowest_index]['min_temp'] - self.indexes[highest_index]['min_temp']
        self.deltas['rainfall'] = self.indexes[lowest_index]['rainfall'] - self.indexes[highest_index]['rainfall']
        self.deltas['chance_of_rain'] = self.indexes[lowest_index]['chance_of_rain']\
                                        - self.indexes[highest_index]['chance_of_rain']


files = get_files(relative_path='../weather-data')

weather_objects = dict()

for file in files:
    data = get_xml(file)
    for period in data.area.find_all('forecast-period'):
        datename = period.attrs['start-time-local'][:10]
        date = datetime.strptime(datename, "%Y-%m-%d")
        if datename not in weather_objects:
            weather_objects[datename] = WeatherEntry(date)

        weather_objects[datename].add_index(period)


faulty_object_keys = []
for k,v in weather_objects.items():
    if v.lowest_index == v.highest_index:
        faulty_object_keys.append(k)

for key in faulty_object_keys:
    weather_objects.pop(key)


weather_variable = 'max_temp'
x_data = []
y_data = []
for obj in weather_objects.values():
    x_data.append(obj.date)
    highest_index = obj.highest_index
    while not obj.indexes[str(highest_index)][weather_variable] and highest_index > obj.lowest_index:
        highest_index -= 1
        while str(highest_index) not in obj.indexes:
            highest_index -= 1
    lowest_index = obj.lowest_index
    while not obj.indexes[str(lowest_index)][weather_variable] and lowest_index < highest_index:
        lowest_index += 1
        while str(lowest_index) not in obj.indexes:
            lowest_index += 1
    y_data.append(obj.indexes[str(lowest_index)][weather_variable] - obj.indexes[str(highest_index)]['max_temp'])


fig = go.Figure([go.Scatter(x=x_data, y=y_data)])
fig.show()