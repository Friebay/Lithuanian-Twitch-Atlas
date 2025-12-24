# Lithuanian Twitch Atlas
Various Lithuanian Twitch communities statistics

This project is inspired by the [Twitch Atlas](https://github.com/KiranGershenfeld/VisualizingTwitchCommunities).

## Getting Started

### 1. Requirements

- Python 3
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Setup

- Copy `.env.example` to `.env`:
  ```bash
  cp .env.example .env
  ```
- Open `.env` and add your Twitch Client ID and Secret (get them from [Twitch Developer Console](https://dev.twitch.tv/console)).

### 3. Usage

Run the scripts in the following order:

1.  Get the list of active Lithuanian streamers from `twitchers.lt`.
    ```bash
    python streamers/get_twitchers.py
    ```

2.  Fetch Twitch user IDs for the streamers found in step 1.
    ```bash
    python streamers/get_twitch_streamers.py
    ```
    *Choose option 2 to fetch IDs.*

3.  Get detailed data (last broadcast, etc.) from `api.ivr.fi`.
    ```bash
    python streamers/get_ivr_fi_log.py
    ```

4.  Filter for streamers active in the last 14 days and update `configs/config.json`.
    ```bash
    python streamers/get_active_streamers.py
    ```

## Directory Structure

- `streamers/`: Python scripts for data fetching.
- `configs/`: configuration files for [rustlog](https://github.com/boring-nick/rustlog).
- `streamers/ivr-fi-logs/`: JSON logs of streamer data.

## TODO

- Create the Twitch Atlas itself.
- Add option to skip fetching user IDs with Twitch API and fetch with ivr.fi API.

