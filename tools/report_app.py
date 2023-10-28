from datetime import date, timedelta
import requests
from pprint import pprint


URL_BASE = "http://wastewater.jrmontag.xyz"
API_ROOT = "/api/v1"
UTILITIES_PATH = f"{URL_BASE}{API_ROOT}/utilities"
SAMPLES_PATH = f"{URL_BASE}{API_ROOT}/samples"


def main():
    utilities = requests.get(UTILITIES_PATH).json()["utilities"]
    prompt = "\nSee available [u]tilities, or view latest [d]ata? "
    choice: str = input(prompt)
    while choice:
        selection = choice.lower().strip()
        if selection == "u":
            pprint(utilities)
            print("\n (TIP: copy the name of your desired utility for easy entry)\n")
        elif selection == "d":
            # prompt for utility and date range
            utility: str = input("Name of wastewater utility to query: ")
            # handle included whitespace and single quotes
            utility = utility.lstrip("' ").rstrip("' ")
            if utility not in utilities:
                print(f"Invalid utility: {utility}. Please try again.")
                break
            lookback: str = input("Select lookback period: [3] mo, [12] mo, [a]ll time: ")
            end = date.today()
            match lookback:
                case "3" | "12":
                    diff = timedelta(days=30 * int(lookback))
                case "a":
                    diff = timedelta(days=30 * 12 * 3)
                case _:
                    print(f"Invalid lookback: {lookback}")
                    break
            start = end - diff
            param_query = f"?utility={utility}&start={start.isoformat()}&end={end.isoformat()}"
            resp = requests.get(SAMPLES_PATH + param_query).json()
            cleaned_result = [data for data in resp["samples"] if data[1] is not None]
            pprint(cleaned_result)
        else:
            print(f"Invalid selection: {choice}")
        choice: str = input(prompt)


if __name__ == "__main__":
    main()
