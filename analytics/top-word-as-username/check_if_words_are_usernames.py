import requests
import time
from typing import Dict, List, Set
from get_one_word_messages import get_top_one_word_messages
from twitch import TwitchValidator


def check_username_availability(words: List[str]) -> List[str]:
    """
    Checks which words from the provided list are NOT currently taken as Twitch usernames.

    Uses the api.ivr.fi service to batch check username existence.
    """
    # Twitch username requirements:
    # 4-25 chars, alphanumeric or underscores, cannot start with underscore.
    allowed_word_list = []
    for word in words:
        if (
            4 <= len(word) <= 25
            and word[0] != "_"
            and all(c.isalnum() or c == "_" for c in word)
        ):
            allowed_word_list.append(word)

    chunk_size = 50
    list_of_lists = [
        allowed_word_list[i : i + chunk_size]
        for i in range(0, len(allowed_word_list), chunk_size)
    ]

    taken_usernames_lower: Set[str] = set()
    session = requests.Session()

    print(
        f"Checking {len(allowed_word_list)} valid words in {len(list_of_lists)} batches"
    )

    for i, list_chunk in enumerate(list_of_lists):
        unique_chunk_lower = sorted(list(set(w.lower() for w in list_chunk)))
        logins = ",".join(unique_chunk_lower)

        try:
            resp = session.get(
                "https://api.ivr.fi/v2/twitch/user", params={"login": logins}
            )
            resp.raise_for_status()
            batch_results = resp.json()

            if isinstance(batch_results, list):
                for user in batch_results:
                    if isinstance(user, dict) and "login" in user:
                        taken_usernames_lower.add(user["login"].lower())

            print(
                f"Batch {i+1}/{len(list_of_lists)}: Checked {len(unique_chunk_lower)} words."
            )
        except requests.RequestException as e:
            print(f"Batch {i+1} failed: {e}")

        time.sleep(1)

    available_words = [
        word for word in allowed_word_list if word.lower() not in taken_usernames_lower
    ]

    return available_words


def check_username_availability_twitch(words: List[str]) -> List[str]:
    """
    Checks which words are available using the Twitch API.

    Args:
        words: A list of candidate usernames.

    Returns:
        A list of usernames that are confirmed available by Twitch.
    """
    validator = TwitchValidator()
    available_words = []

    print(f"Verifying {len(words)} candidates with Twitch API...")

    for i, word in enumerate(words):
        is_available = validator.is_username_available(word)

        if is_available is True:
            available_words.append(word)
            status = "AVAILABLE"
        elif is_available is False:
            status = "TAKEN"
        else:
            status = "ERROR/FAILED"

        print(f"[{i+1}/{len(words)}] {word} | {status}")

        time.sleep(0.5)

    return available_words


if __name__ == "__main__":
    NUMBER_OF_WORDS = 100

    print(f"Extracting top {NUMBER_OF_WORDS} messages")
    top_words = get_top_one_word_messages(NUMBER_OF_WORDS)

    if not top_words:
        print("No words extracted. Exiting.")
    else:
        word_list = list(top_words.keys())
        print(f"Extracted {len(word_list)} candidates")

        # Batch check through ivr.fi API
        print("\nivr.fi batch check")
        initially_available = check_username_availability(word_list)
        print(f"Found {len(initially_available)} potential candidates.")

        # Verification through Twitch API
        print("\nTwitch verification")
        if initially_available:
            available = check_username_availability_twitch(initially_available)
        else:
            available = []

        print(f"Available Twitch usernames from top {NUMBER_OF_WORDS} messages")
        if available:
            # Sort by count (descending), then by word (alphabetically)
            available_sorted = sorted(available, key=lambda x: (-top_words[x], x))
            for word in available_sorted:
                print(f"{word}: {top_words[word]}")
        else:
            print("No available usernames found in the top 100.")
