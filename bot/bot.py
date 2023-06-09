import datetime as dt
from os import environ

import config
import discord
import requests
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
POLL_OPTION_EMOJIS = ["1️⃣", "2️⃣"]

SENT_MESSAGE_IDS = []

def create_petition(title, content, option_1, option_2, countdown):
    data = {
        "title": title,
        "content": content,
        "option_1": option_1,
        "option_2": option_2,
        "countdown": countdown
        }
    
    response = requests.post(f'{config.API_URL}/petitions', json= data)
    return response.json()
    

def update_petition(petition_id, data):
    requests.patch(f'{config.API_URL}/petitions/{petition_id}', json= data)


@client.event
async def on_message(message):
    global POLL_OPTION_EMOJIS
    if message.content.startswith("!create"):
        params = message.content.split(";")
        title = params[0].replace("!create", "").strip()
        content = params[1].strip()
        options = [x.strip() for x in params[2].strip().split(",")]
        orig_options = options
        options_count = len(options)
        countdown = params[3]

        try:
            countdown = int(countdown)
        except Exception as e:
            pass

        error = validate_params(title, content, options, countdown)

        result = create_petition(title, content, orig_options[0], orig_options[1], countdown)
        petition_id = result['id']

        if error is not None:
            embed = discord.Embed(
                title="Error", description=error, color=discord.Color.red())
            sent = await message.channel.send(embed=embed)
            return

        for i in range(len(options)):
            options[i] = f"{POLL_OPTION_EMOJIS[i]} {options[i]}"
        options = '\n'.join(options)

        embed = discord.Embed(
            title=f"PETITION: {title}", description=f"**{content}\n{options}**", color=0x12ff51)
        sent = await message.channel.send(embed=embed)

        POLL_OPTION_EMOJIS = ["1️⃣", "2️⃣"]
        for i in range(options_count):
            await sent.add_reaction(POLL_OPTION_EMOJIS[i])

        SENT_MESSAGE_IDS.append(sent.id)
        end_time = dt.datetime.utcnow() + dt.timedelta(seconds=int(countdown)*60)

        @tasks.loop(seconds=1)
        async def update_countdown():
            remaining_time = (end_time - dt.datetime.utcnow()).total_seconds()

            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)

                description = f"**{content}**\n{options}\n\n*La pétition prend fin dans {minutes:02d}:{seconds:02d}*"
                embed = discord.Embed(
                    title=f"PETITION: {title}", description=description, color=0x12ff51)
                await sent.edit(embed=embed)

            else:
                sent_message = await message.channel.fetch_message(sent.id)

                petition_results_count = {}
                total_reactions = 0

                for reaction in sent_message.reactions:
                    for ind, emoji in enumerate(POLL_OPTION_EMOJIS):
                        if reaction.emoji == emoji:
                            petition_results_count[ind+1] = reaction.count - 1
                            if reaction.count > 1:
                                total_reactions += 1
                

                petition_results_message = ""

                for ind, count in enumerate(petition_results_count):
                    try:
                        perc = round(petition_results_count[ind+1]/total_reactions * 100)
                    except ZeroDivisionError:
                        perc = 0
                    petition_results_message += f"{orig_options[ind]} ~ {perc}% ({petition_results_count[ind+1]} votes)\n"

                update_petition(petition_id, {
                    "is_closed": True,
                    "votes_option_1": petition_results_count[1],
                    "votes_option_2": petition_results_count[2]
                })

                embed = discord.Embed(
                    title=f"RESULTATS DE LA PETITION: {title}", description=petition_results_message, color=0x13a6f0)
                await message.channel.send(embed=embed)

                await sent_message.delete()
                update_countdown.cancel()

        update_countdown.start()

    @client.event
    async def on_raw_reaction_add(payload):
        global SENT_MESSAGE_IDS
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        guild = message.guild
        member = await guild.fetch_member(payload.user_id)

        if payload.member.bot:
            return

        sent_by_bot = False
        for i in SENT_MESSAGE_IDS:
            if i == message.id:
                sent_by_bot = True
                break
        if not sent_by_bot:
            return

        if payload.emoji.name not in POLL_OPTION_EMOJIS:
            await message.remove_reaction(payload.emoji.name, member)
            return

        user_reaction_count = 0
        for r in message.reactions:
            async for u in r.users():
                if u.id == payload.user_id:
                    user_reaction_count += 1
                    if user_reaction_count > 1:
                        await message.remove_reaction(payload.emoji.name, member)
                        break


def validate_params(title, content, options, countdown):
    if title == "":
        return "Le nom de la pétition ne doit pas être vide"
    if content == "":
        return "La question ne doit pas être vide"
    if len(options) < 2:
        return "Il doit y avoir au minimum 2 options"
    if len(options) > 2:
        return "Il doit y avoir au maximum 2 options"
    if not isinstance(countdown, int):
        return "La valeur du compte à rebours doit être un nombre entier"

    return None


if __name__ == "__main__":
    client.run(config.DISCORD_TOKEN)
