import json
import sys
import random
import time
from datetime import datetime
from http.client import HTTPSConnection

CONFIG_FILE = "config.txt"
MESSAGES_FILE = "messages.txt"


def get_timestamp():
    return "[" + str(datetime.now().strftime("%H:%M:%S")) + "]"


def random_sleep(duration, min_random, max_random):
    sleep_duration = max(round((duration + random.uniform(min_random, max_random)) * 10) / 10, 0)
    print(f"{get_timestamp()} Waiting {sleep_duration} seconds")
    time.sleep(sleep_duration)


def read_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            token = lines[0].strip()
            channel = lines[1].strip()
            return token, channel
    except Exception as error:
        if not isinstance(error, FileNotFoundError):
            print(f"{get_timestamp()} Error reading config: {error}")
    return None, None


def write_config(token, channel):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            file.write(f"{token}\n{channel}")
    except Exception as error:
        print(f"{get_timestamp()} Error writing config: {error}")
        input("Press Enter to exit...")
        sys.exit()


def configure():
    try:
        token = input("Discord token: ")
        channel = input("Discord channel ID: ")
        write_config(token, channel)
        print("\nWritten config to config.txt. Continuing with new configuration...\n\n")
        return token, channel
    except Exception as error:
        print(f"{get_timestamp()} Error configuring: {error}")
        input("Press Enter to exit...")
        sys.exit()


def set_channel():
    config = read_config()
    if config:
        try:
            token = config[0]
            channel = input("Discord channel ID: ")
            write_config(token, channel)
            print("\nWritten config to config.txt. Continuing with new configuration...\n\n")
            return token, channel
        except Exception as error:
            print(f"{get_timestamp()} Error setting channel: {error}")
            input("Press Enter to exit...")
            sys.exit()
    else:
        print("No existing config found. Please run the configuration setup first.")
        input("Press Enter to exit...")
        sys.exit()

def show_help():
    print("Usage:")
    print("  'python automessage.py'               :  Runs the automessenger. Type in the settings and take a back seat.")
    print("  'python automessage.py --config'      :  Configure settings.")
    print("  'python automessage.py --channel'     :  Set channel to send messages to.")
    print("  'python automessage.py --help'        :  Show help (You just did that lol).\n\n")


def send_message(token, channel, content, messages_remaining, message_amount):
    payload = json.dumps({"content": content})
    headers = {"content-type": "application/json", "authorization": token, "host": "discord.com"}

    while True:
        try:
            connection = HTTPSConnection("discord.com", 443)
            connection.request("POST", f"/api/v9/channels/{channel}/messages", payload, headers)
            response = connection.getresponse()
            body = response.read().decode()
            connection.close()
        except Exception as error:
            print(f"{get_timestamp()} Network error sending message: {error}")
            return False

        if response.status == 429:
            try:
                retry_after = json.loads(body).get("retry_after", 1)
            except Exception:
                retry_after = 1
            print(f"{get_timestamp()} Rate-limited. Retrying in {retry_after}s")
            time.sleep(retry_after + 0.05)
            continue

        if 199 < response.status < 300:
            if messages_remaining >= 0:
                print(f"{get_timestamp()} Sent: {message_amount - messages_remaining} of {message_amount} '{content}'")
            else:
                print(f"{get_timestamp()} Sent: '{content}'")
            return True

        print(f"{get_timestamp()} Failed to send ({response.status}): {body}")
        return False


def get_arguments():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--config":
            configure()
        elif sys.argv[1] == "--channel":
            set_channel()
        elif sys.argv[1] == "--help":
            show_help()
            sys.exit()
            
def main():
    get_arguments()

    config = read_config()
    if config is None or not config[0] or not config[1]:
        print("No config was found. Running configuration setup.")
        config = configure()
    token, channel = config

    print("-----[  Welcome!  ]-----")
    print("Please set your session delay time, random offset and message amount!")
    print(f"Messages will be sent to channel: {channel}.\n")

    sleep_time = float(input("Delay (seconds) between messages: "))
    random_offset = float(input("Random offset (seconds) applied to delay: "))
    message_amount = int(input("Amount of messages to send before stopping (-1 = send all): "))
    messages_remaining = message_amount
    if message_amount < 0:
        loop_amount = int(input("Amount of loops to do through all messages (-1 = never stop): "))
        loops_remaining = loop_amount
    else:
        loop_amount = -1
        loops_remaining = -1

    print("\n\n-----[ Sending... ]-----")

    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as file:
            messages = file.read().splitlines()
    except FileNotFoundError:
        print(f"{get_timestamp()} Messages file not found.")
        input("Press Enter to exit...")
        sys.exit()
    
    while loops_remaining != 0 and messages_remaining != 0:
        for message in messages:
            if messages_remaining != 0:
                messages_remaining -= 1
                send_message(token, channel, message, messages_remaining, message_amount)
                random_sleep(sleep_time, -random_offset, random_offset)
        if loops_remaining > 0:
            loops_remaining -= 1
            print(f"Finished sending {message_amount} messages! Loops remaining: {loops_remaining}")
    
    if message_amount > 0:
        print(f"Finished sending {message_amount} messages!")
    elif loop_amount > 1:
        print(f"Finished sending {loop_amount} loops of messages!")
    else:
        print("Finished sending all messages!")
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()