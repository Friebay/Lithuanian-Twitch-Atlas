import requests
import json
from pathlib import Path


def fetch_twitchers():
    """Fetches all streamers from twitchers.lt"""
    print("Fetching data from twitchers.lt...")
    try:
        response = requests.get("https://twitchers.lt/api/users/all")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

    twitchers = []
    for streamer in response.json():
        if streamer.get("platform") == "Twitch":
            twitchers.append(streamer["username"])

    print(f"Found {len(twitchers)} Twitch streamers on twitchers.lt")
    return twitchers


def load_local_streamers(file_path):
    """Loads local streamers data from JSON file."""
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {file_path}: {e}")
        return []


def main():
    # Define paths relative to this script
    current_dir = Path(__file__).resolve().parent
    data_file = current_dir / "twitch_streamers_with_ids.json"

    # Get online data
    twitchers = fetch_twitchers()

    # Get local data
    local_data = load_local_streamers(data_file)
    local_usernames = [s["username"] for s in local_data]

    print(f"Locally stored streamers: {len(local_usernames)}")

    # Find missing streamers
    changed = False
    for streamer in twitchers:
        if streamer not in local_usernames:
            print(f"Adding new streamer: {streamer}")
            new_streamer = {"username": streamer, "twitch_id": "", "found": False}
            local_data.append(new_streamer)
            # Keep track to avoid duplicates
            local_usernames.append(streamer)
            changed = True

    # Save if changes made
    if changed:
        try:
            with open(data_file, "w", encoding="utf-8") as file:
                json.dump(local_data, file, indent=2, ensure_ascii=False)
            print("Successfully updated twitch_streamers_with_ids.json")
        except IOError as e:
            print(f"Error saving data: {e}")
    else:
        print("No new streamers found. File is up to date.")


if __name__ == "__main__":
    main()
