import sys
import json

# Ensure a file path is provided as an argument
if len(sys.argv) != 2:
    print("Usage: run_my_py <path_to_json_file>")
    sys.exit(1)

def remove_duplicates(data_json):
    levels_till_now = []
    cleaned_json = {"60":[], "240":[], "1D":[], "1W":[], "1M":[]}
    for i in priority_order:
        for j in data_json[i]:
            present = False
            for k in levels_till_now:
                if abs(j-k)/j < 0.001:
                    present = True
                    break
            if not present:
                levels_till_now.append(j)
                cleaned_json[i].append(j)
    return cleaned_json

cleaned_levels = {"60":[], "240":[], "1D":[], "1W":[], "1M":[]}
priority_order = ["1M", "1W", "1D", "240", "60"]
try:
    # Open and load the JSON file
    input_json = json.loads(sys.argv[1])
    kaam_ki_json = input_json['payload']['sources']
    for i in kaam_ki_json:
        if kaam_ki_json[i]['state']['type'] == 'LineToolFibRetracement':
            continue
        print(kaam_ki_json[i]['state']['type'], kaam_ki_json[i]['state']['points'])
        if kaam_ki_json[i]['state']['state']['interval'] in cleaned_levels:
            for point in kaam_ki_json[i]['state']['points']:
                cleaned_levels[kaam_ki_json[i]['state']['state']['interval']].append(point['price'])
            if kaam_ki_json[i]['state']['type'] == 'LineToolRectangle':
                points = kaam_ki_json[i]['state']['points']
                if (points[0]['price'] - points[1]['price']) > (0.002 * points[0]['price']):
                    cleaned_levels[kaam_ki_json[i]['state']['state']['interval']].append((points[0]['price'] + points[1]['price'])/2)
    cleaned_levels_new = remove_duplicates(cleaned_levels)
    print(cleaned_levels_new)
except FileNotFoundError:
    print(f"File not found: {sys.argv[1]}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Invalid JSON file: {e}")
    sys.exit(1)