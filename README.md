# Discord Server Archiver

This is a Discord bot that archives entire servers, storing every message in a SQLite database for easy querying.

## Installation

1. Create a Discord bot in the Developer portal: https://discord.com/developers/applications.

2. Add the bot to your server using the generated OAUTH2 URL. Since I'm hosting it myself and using it on my server I'd
   just give it Administrator permissions. Otherwise, my best guess is that it needs to view and manage messages. For example:
   https://discord.com/oauth2/authorize?client_id=1016161382653247569&permissions=292057901056&integration_type=0&scope=bot

4. Install Python: https://www.python.org/downloads/

5. Clone the repo:

```bash
git clone https://github.com/TheNathanSpace/DiscordServerArchiver
cd DiscordServerArchiver
```

5. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

6. Define your bot's secret key in the variable `key` in the module `secrets`:

```python
key = "asdfasdgraha4535h5h3h5.25yhbas.5h23qaz6uaq35yraq3y35aq"
```

7. Run the bot:

```bash
python bot.py
```

## Commands

`!update_archive` archives every message in the server, storing them in an SQLite database.

`!count_reactions` queries the local database, counts how many times each user has used each reaction, and saves the
results as a `.json` file.
