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
    print(f"{get_timestamp()} `-> Sleeping for {sleep_duration} seconds")
    time.sleep(sleep_duration)


def read_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"{get_timestamp()} config file not found.")
        return None


def write_config(token, channel_id):
    try:
        with open(CONFIG_FILE, "w") as file:
            file.write(f"{token}\n{channel_id}")
    except Exception as e:
        print(f"{get_timestamp()} Error writing config: {e}")
        exit()


def configure_config():
    try:
        token = input("Discord token: ")
        channel_id = input("Discord channel ID: ")
        write_config(token, channel_id)
        print("Written config to config.txt, please rerun to start!")
    except Exception as e:
        print(f"{get_timestamp()} Error configuring: {e}")
        exit()


def set_channel():
    config = read_config()
    if config:
        token = config[0]
        channel_id = input("Discord channel ID: ")
        write_config(token, channel_id)
        print("Written config to config.txt, please rerun to start!")


def show_help():
    print("Showing help for discord-auto-messenger")
    print("Usage:")
    print("  'python3 automessage.py'               :  Runs the automessenger. Type in the settings and take a back seat.")
    print("  'python3 automessage.py --config'      :  Configure settings.")
    print("  'python3 automessage.py --setC'        :  Set channel to send messages to.")
    print("  'python3 automessage.py --help'        :  Show help")


def send_message(conn, channel_id, message_data, header_data, message, messages_remaining, message_amount):
    try:
        conn.request("POST", f"/api/v6/channels/{channel_id}/messages", message_data, header_data)
        resp = conn.getresponse()
        body = resp.read().decode()

        if 199 < resp.status < 300:
            # Successful send
            if messages_remaining >= 0:
                print(f"{get_timestamp()} Sent message: {message_amount - messages_remaining} of {message_amount} '{message}'")
            else:
                print(f"{get_timestamp()} Sent message: '{message}'")
            return True

        elif resp.status == 429:
            # Rate limit
            try:
                error_data = json.loads(body)
                retry_after = error_data.get("retry_after", 1)
            except Exception:
                retry_after = 1
            print(f"{get_timestamp()} !! Rate limited. Retrying after {retry_after:.2f} seconds...")
            time.sleep(retry_after + 0.1)
            return False

        else:
            print(f"{get_timestamp()} !! Failed to send (status {resp.status}): {body}")
            return True 

    except Exception as e:
        print(f"{get_timestamp()} !! Error sending message: {e} | {message_data}")
        return True


def get_connection():
    return HTTPSConnection("discordapp.com", 443)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--config" and input("Configure? (y/n) ") == "y":
            configure_config()
            return
        elif sys.argv[1] == "--setC" and input("Set channel? (y/n) ") == "y":
            set_channel()
            return
        elif sys.argv[1] == "--help":
            show_help()
            return

    config = read_config()
    if not config or len(config) != 2:
        print(f"{get_timestamp()} Invalid or missing config file. Please reconfigure.")
        configure_config()
        return

    token, channel_id = config

    header_data = {
        "content-type": "application/json",
        "authorization": token,
        "host": "discordapp.com",
    }

    print("-----[  Welcome!  ]-----")
    print("Please initialise your session delay time, random offset and message amount!")
    print(f"Messages will be sent to channel: {channel_id}.\n")

    sleep_time = float(input("Delay (in seconds) between messages: "))
    random_offset = float(input("Random offset (in seconds) applied to delay: "))
    message_amount = int(input("Amount of messages to send before stopping (-1 = send all): "))
    messages_remaining = message_amount
    if message_amount < 0:
        loop_amount = int(input("Amount of loops to do through all messages (-1 = never stop): "))
        loops_remaining = loop_amount
    else:
        loop_amount = -1
        loops_remaining = -1

    print("\n\n-----[ Sending... ]-----")

    while loops_remaining != 0 and messages_remaining != 0:
        try:
            with open(MESSAGES_FILE, "r", encoding="utf-8") as file:
                messages = file.read().splitlines()
        except FileNotFoundError:
            print(f"{get_timestamp()} Messages file not found.")
            return

        loops_remaining -= 1
        for message in messages:
            if messages_remaining != 0:
                messages_remaining -= 1
                message_data = json.dumps({"content": message})
                conn = get_connection()
                send_message(conn, channel_id, message_data, header_data, message, messages_remaining, message_amount)
                conn.close()
                random_sleep(sleep_time, -random_offset, random_offset)

    print(f"\n\n{get_timestamp()} -----[    Done!   ]-----")
    if message_amount > 0:
        print("Finished sending {message_amount} messages!")
    elif loop_amount > 1:
        print("Finished sending {loop_amount} loops of messages!")
    else:
        print("Finished sending all messages!")
    input("\nPress [Enter] to close...")


if __name__ == "__main__":
    main()