import json
from datetime import datetime

data = [{"dt": 123456789, "precipitation": 0}] * 120

with open("./producer/data/23_26_11_14_42.json", "r") as f:
    data.extend(json.load(f)["minutely"])

with open("./producer/data/23_26_11_15_42.json", "r") as f:
    data.extend(json.load(f)["minutely"])

data = data * 2

for i in range(240):
    # print([p["precipitation"] for p in data[i:i + 60]])
    print(
        datetime.fromtimestamp(data[i]["dt"]),
        "-",
        datetime.fromtimestamp(data[i + 60]["dt"]),
        end=": ",
    )
    print(sum(p["precipitation"] for p in data[i : i + 60]))
    # print()

# precipitation_sum = sum(p["precipitation"] for p in data)
# print(precipitation_sum)
