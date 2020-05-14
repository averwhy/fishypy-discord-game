import json

fishy_json = open("C:\\Users\\aver\\Documents\\GitHub\\fishy-discord-game\\fishes.json")
json_data = json.load(fishy_json)
print(json_data[0])
for i in json_data[0]:
    print(i[2])
