# Discord Auto Messenger

This Python script can send messages on your account to any channel you're in. You can also customize the delay, random offset, message amount and optionally the loop amount.

## ⭐ Features

* Automatically sends messages to a specified Discord channel
* Customizable sleep time between messages
* Choose random offset to make message timing less predictable
* Pick message amount and loop count
* Handles rate-limits

---

## 📦 Setup

Download the folder, and run `hardlyknowifier.py`.
You need Python 3 installed, no extra dependencies.

The first time you run the script, it will ask you for:

1. **Your Discord token**
2. **A Discord Channel ID**
3. **Whether to ignore your own messages**

These are stored in `config.txt`. Rerun the script after the file is made.

> **Important:**
> Your Discord token gives full access to your account.
> **Do NOT share, upload or commit it anywhere else.**
> [How to get your Discord token](https://www.youtube.com/watch?v=5SRwnLYdpJs)

## ⚡ Usage

When you run the script, it will give you a short setup:

1. **Sleep Time**: Time to wait between messages (in seconds).
2. **Random Offset**: Random time added or subtracted from the sleep time (in seconds).
3. **Message Amount**: Number of messages to send before stopping (-1 to send all).
4. **Loop Amount**: Number of times to loop through all messages (-1 to never stop).

## ⚙️ Options

The script offers the following options:

`--config`: Change your settings by setting your Discord token and Discord channel ID:
```
python automessage.py --config
```

`--channel`: Set the channel for that the bot will send messages to:
```
python automessage.py --channel
```

`--help`: Show argument help information for the script:
```
python automessage.py --help
```

## 🙏 Notes

Having a bot using your account is against Discords TOS and not allowed by most servers, so probably keep it to you and some friends, or use at your own risk.

`config.txt` has your Discord token. So be extremely careful when sharing the project folder.

This was originally a fork of [xRiddin/Discord-Auto-message](https://github.com/xRiddin/Discord-Auto-message), make sure to check them out too! And feel free to fork or make a PR if you manage to improve the script.

You are free to use the project however you want *(just try not to annoy people too much lol)*, it would be appreciated if you would provide credit when modifying, redistributing or showcasing my work.