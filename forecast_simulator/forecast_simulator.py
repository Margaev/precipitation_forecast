import json
import os
from datetime import datetime, timedelta
from typing import Iterable

DATA_DIR = "data"


class ForecastSimulator:
    def __init__(self):
        self._forecast_data = self._get_initial_forecast_data()

    @staticmethod
    def _get_initial_forecast_data():
        forecast_data = []
        for file_name in os.listdir(DATA_DIR):
            if not file_name.endswith(".json"):
                continue
            with open(os.path.join(DATA_DIR, file_name), "r") as f:
                data = json.load(f)
                for entry in data["minutely"]:
                    forecast_data.append(entry)
        forecast_data = sorted(forecast_data, key=lambda x: x["dt"])
        return [entry["precipitation"] for entry in forecast_data]

    @staticmethod
    def _get_timestamp_range(start_timestamp: datetime) -> Iterable[int]:
        for minutes in range(1, 61):
            ts = start_timestamp + timedelta(seconds=minutes * 60)
            yield int(ts.replace(second=0, microsecond=0).timestamp())

    def get_current_forecast(self, current_timestamp):
        forecast = {
            "lat": 52.0845,
            "lon": 5.1155,
            "timezone": "Europe/Amsterdam",
            "timezone_offset": 3600,
            "minutely": [],
        }
        for ts in self._get_timestamp_range(current_timestamp):
            forecast["minutely"].append(
                {
                    "dt": ts,
                    "precipitation": self._forecast_data[
                        ts // 60 % len(self._forecast_data)
                    ],
                }
            )

        return forecast


if __name__ == "__main__":
    # Test
    forecast_simulator = ForecastSimulator()
    print(
        json.dumps(
            forecast_simulator.get_current_forecast(
                datetime.now().replace(hour=23, minute=4)
            ),
            indent=4,
        )
    )
    print(
        json.dumps(
            forecast_simulator.get_current_forecast(
                datetime.now().replace(hour=23, minute=6)
            ),
            indent=4,
        )
    )
