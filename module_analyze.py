import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from nextcord import Guild, TextChannel, Message
from nextcord.ext import commands
from nextcord.ext.commands import Context


class SavedMessage:
    def __init__(self, message: Message):
        self.message_timestamp: float = message.created_at.timestamp()
        self.message_id: int = message.id
        self.channel_id: int = message.channel.id
        self.author_id: int = message.author.id
        attachment_list = message.attachments
        self.attachment_url_list = []
        if len(attachment_list) > 0:
            for attachment in attachment_list:
                self.attachment_url_list.append(attachment.url)

        self.message_text: str = "" + message.content

    async def get_reactions(self, message: Message):
        reactions = message.reactions
        new_reaction_list = {}
        reactions = message.reactions
        for reaction in reactions:
            if type(reaction.emoji) is str:
                name = reaction.emoji
                id = None
            else:
                id = reaction.emoji.id
                name = reaction.emoji.name

            users = await reaction.users().flatten()
            for user in users:
                if user.id not in new_reaction_list:
                    new_reaction_list[user.id] = []
                if id:
                    emoji_dict = {"name": name, "id": id}
                    new_reaction_list[user.id].append(emoji_dict)
                else:
                    new_reaction_list[user.id].append(name)

        self.reaction_dict = new_reaction_list


class CogArchive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_sender = None

    def create_database(self, guild_id):
        connection = sqlite3.connect(f'database_{guild_id}.db')
        cursor = connection.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS messages(message_id integer PRIMARY KEY, channel_id integer, author_id integer, message_timestamp float, attachment_url_list text, message_text text, reaction_list text);')
        connection.commit()

    @commands.command()
    async def archive(self, context: Context):
        logging.info(f"Started archiving messages from [{context.guild.name}]")
        latest = await context.message.reply("Archiving server!")
        with context.typing():
            guild: Guild = context.guild
            text_channel_dict = {}
            for channel in guild.text_channels:
                text_channel_dict[channel.id] = None
            for thread in guild.threads:
                text_channel_dict[thread.id] = None

            self.create_database(context.guild.id)
            connection = sqlite3.connect(f'database_{context.guild.id}.db')
            cursor = connection.cursor()
            channel_ids = cursor.execute('SELECT DISTINCT channel_id FROM messages;')
            for channel_id in channel_ids:
                channel_id = channel_id[0]
                if channel_id in text_channel_dict:
                    text_channel_dict[channel_id] = True

            for channel_id in text_channel_dict:
                if text_channel_dict[channel_id] is not None:
                    latest_message = cursor.execute(
                        'SELECT message_id FROM messages WHERE channel_id = ? ORDER BY message_timestamp DESC;',
                        (channel_id,)).fetchone()
                    text_channel_dict[channel_id] = latest_message[0]

            text_channel: TextChannel
            for text_channel_id in text_channel_dict:
                text_channel = guild.get_channel(text_channel_id) or guild.get_thread(text_channel_id)
                if text_channel is None:
                    logging.info(f"Error: Channel [{text_channel_id}] is null")
                    continue

                logging.info(f"On channel: [{text_channel.name}]")
                latest = await latest.reply(f"On channel: [{text_channel.name}]")

                message_number = 0

                after = None
                if text_channel_dict[text_channel_id] is not None:
                    message_id = text_channel_dict[text_channel_id]
                    try:
                        latest_message: Message = await text_channel.fetch_message(message_id)
                        after = latest_message.created_at
                        logging.info("Getting all messages after " + after.date().strftime("%B %d, %G"))
                    except Exception as e:
                        logging.info(
                            f"Error getting latest message in channel [{text_channel.name}]. The bot probably doesn't have access to it.")
                        latest = await latest.reply(f"Error getting latest message in channel [{text_channel.name}]. The bot probably doesn't have access to it.")
                try:
                    async for message in text_channel.history(limit=None, oldest_first=True, after=after):
                        message_number += 1
                        logging.info(f"On message #{message_number}", end="\r")
                        saved_message = SavedMessage(message)
                        while True:
                            try:
                                await saved_message.get_reactions(message)
                                break
                            except Exception as e:
                                logging.info(f"Error getting reactions; retrying: {e}")

                        to_insert = (
                            saved_message.message_id, saved_message.channel_id, saved_message.author_id,
                            saved_message.message_timestamp, json.dumps(saved_message.attachment_url_list),
                            saved_message.message_text, json.dumps(saved_message.reaction_dict)
                        )
                        cursor.execute(
                            'INSERT INTO messages(message_id, channel_id, author_id, message_timestamp, attachment_url_list, message_text, reaction_list) VALUES(?,?,?,?,?,?,?) ON CONFLICT(message_id) DO NOTHING;',
                            to_insert)

                        connection.commit()
                except:
                    logging.info(
                        f"Error getting messages in channel [{text_channel.name}]. The bot probably doesn't have access to it.")
                    latest = await latest.reply(
                        f"Error getting messages in channel [{text_channel.name}]. The bot probably doesn't have access to it.")

            logging.info(f"Finished scraping messages from [{context.guild.name}]")
            await latest.reply("Finished archiving server!")

    @commands.command()
    async def count_reactions(self, context: Context):
        logging.info(f"Started counting reactions for [{context.guild.name}]")
        initial = await context.message.reply("Counting reactions!")
        with context.typing():
            self.create_database(context.guild.id)
            connection = sqlite3.connect(f'database_{context.guild.id}.db')
            cursor = connection.cursor()
            all_rows = cursor.execute('SELECT reaction_list FROM messages WHERE reaction_list != ?;',
                                      ("{}",)).fetchall()
            user_reactions = {}
            for row in all_rows:
                reaction_dict = json.loads(row[0])
                for user in reaction_dict:
                    for reaction in reaction_dict[user]:  # reaction: {"name": "uptrump_old", "id": 730559664625811486}
                        if user not in user_reactions:
                            user_reactions[user] = {}

                        reaction_name = None
                        if type(reaction) is dict:
                            reaction_name = reaction["name"]
                        else:
                            reaction_name = reaction

                        if reaction_name not in user_reactions[user]:
                            user_reactions[user][reaction_name] = 0

                        user_reactions[user][reaction_name] += 1

            new_dict = {}
            for user in user_reactions:
                try:
                    username = await context.guild.fetch_member(user)
                except:
                    username = "Unknown user"

                new_dict[f"{username} ({user})"] = dict(
                    sorted(user_reactions[user].items(), key=lambda item: item[1], reverse=True))

            Path(f"reactions_{datetime.now().timestamp()}.json").write_text(
                json.dumps(new_dict, indent=4, ensure_ascii=False), encoding="utf8")
            logging.info(f"Finished counting reactions for [{context.guild.name}]")
            await initial.reply("Finished counting reactions!")
