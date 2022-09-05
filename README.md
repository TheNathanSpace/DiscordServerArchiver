# Discord Server Archiver

This is a Discord bot that archives entire servers, storing every message in a SQLite database for easy querying.

## Usage

You'll need to define your secret key in the variable `key` in the module `secrets`. Then, run `bot.py`, and that's
pretty much it.

`!update_archive` archives every message in the server, storing them in an SQLite database.

`!count_reactions` queries the local database, counts how many times each user has used each reaction, and saves the results as a `.json` file.

Bot URL: https://discord.com/api/oauth2/authorize?client_id=1016161382653247569&permissions=65536&scope=bot