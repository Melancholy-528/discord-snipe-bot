import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from better_profanity import profanity
from openai import OpenAI
import os
import random
import re

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="$", intents=intents)

sniped_messages = {}

profanity.load_censor_words()

TRIGGER_GROUPS = [
    {
        "keywords": ["weirdo"],
        "replies": [
            "indeed very weird mf",
            "mute his ass",
            "couldnt be creepier",
            "bro stfu"
        ]
    },
    {
        "keywords": ["cya", "bye", "see you", "cu", "see u", "see ya", "goodbye", "dip"],
        "replies": [
            "you'll be missed",
            "another one dead",
            "better hide",
            "gn dude"
        ]
    },
    {
        "keywords": ["crack"],
        "replies": [
            "nuhuh",
            "that escalated quickly",
            "i definitely heard that"
        ]
    },
    {
        "keywords": ["nut"],
        "replies": [
            "wild thing to say in chat",
            "i'm pretending i didn't read that",
            "caught in 4k"
        ]
    },
    {
        "keywords": ["fuck"],
        "replies": [
            "me?",
            "yo ass needs to be quiet",
            "shushhhh"
        ]
    }
]

def keyword_matches(content: str, keyword: str) -> bool:

    keyword = keyword.lower()
    content = content.lower()

    if " " in keyword:
        return keyword in content

    pattern = rf"\b{re.escape(keyword)}\b"

    return re.search(pattern, content) is not None

def get_trigger_reply(content: str):

    content = content.lower()

    for group in TRIGGER_GROUPS:
        for keyword in group["keywords"]:

            if keyword_matches(content, keyword):
                return random.choice(group["replies"])

    return None

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.event
async def on_message_delete(message: discord.Message):

    if message.author.bot or not message.guild:
        return

    content = (message.content or "").strip()

    if not content:
        return

    if not profanity.contains_profanity(content):
        return

    sniped_messages[message.channel.id] = {
        "author_name": str(message.author),
        "author_avatar": message.author.display_avatar.url,
        "content": content,
        "channel_id": message.channel.id,
        "created_at": message.created_at,
        "deleted_at": datetime.now(timezone.utc)
    }
@bot.command(name="catch")
async def catch(ctx):
    await snipe(ctx)

SARCASM_BANK = [
    "yeah that’s not how reality works but go off",
    "i respect the confidence, not the idea",
    "that statement just lowered my iq a bit",
    "i know what you meant but i’m choosing to ignore it",
    "bro said that like it made sense",
    "interesting take, unfortunately it’s wrong",
    "i’ve seen better logic in a dream",
    "that’s a bold claim for someone so incorrect",
    "you really typed that and hit send huh",
    "i refuse to believe you thought that through",
    "that’s enough internet for today honestly",
    "you might wanna re-evaluate everything you just said",
    "i hear you but i’m pretending i don’t",
    "that sentence felt illegal to read",
    "somehow that made things worse",
    "i’m not mad, just disappointed in the universe",
    "that’s not it chief",
    "you’re speaking but nothing is loading upstairs",
    "i’d agree but then we’d both be wrong",
    "that’s a creative way to be incorrect",
    "you cooked… and burned the kitchen down",
    "this is why aliens don’t talk to us",
    "i lost braincells reading that",
    "you really chose violence against logic",
    "that’s a certified bruh moment",
    "i’m gonna pretend i didn’t see that",
    "that’s not how any of this works",
    "you said that with full confidence too 💀",
    "i can’t tell if you’re joking or just built different (in a bad way)",
    "that idea needs to stay in drafts",
    "i’ve heard better arguments from a toaster",
    "you just typed nonsense in HD",
    "that’s wild coming from you",
    "this is why we can’t have nice things",
    "you might be onto nothing",
    "that’s a skill issue in sentence form",
    "i’m legally required to ignore that",
    "you really thought you did something there",
    "that’s not a take, that’s a detour from reality",
    "i’d explain why that’s wrong but we’d be here all day",
    "your logic left the chat immediately",
    "that statement has no business existing",
    "i’m concerned for your thought process",
    "you just speedran being incorrect",
    "that’s the kind of message you delete after sending",
    "i feel dumber after reading that",
    "you typed that like it was a fact 😭",
    "that’s not a conclusion, that’s a cry for help",
    "i’m not equipped to handle this level of confusion",
    "that’s enough internet for you today",
    "you really woke up and chose confusion",
    "that message violated common sense",
    "i’m sending that back to sender",
    "that’s a creative disaster",
    "you should probably not say that again",
    "this is why aliens avoid Earth"
]

async def generate_sarcastic_reply(user_message: str):

    base = random.choice(SARCASM_BANK)

    extra_twist = random.choice([
        "",
        " anyway...",
        " bro.",
        " 😭",
        " i’m done here.",
        " please rethink that."
    ])

    return base + extra_twist

@bot.event
async def on_message(message: discord.Message):

    if message.author.bot:
        return

    content = message.content.lower()

    trigger_reply = get_trigger_reply(content)

    if trigger_reply:
        await message.channel.send(trigger_reply)

    if bot.user in message.mentions:

        cleaned = message.content
        cleaned = cleaned.replace(f"<@{bot.user.id}>", "")
        cleaned = cleaned.replace(f"<@!{bot.user.id}>", "")
        cleaned = cleaned.strip()

        if not cleaned:

            await message.reply(
                "you pinged me for absolutely nothing",
                mention_author=False
            )

            return

        reply = await generate_sarcastic_reply(cleaned)

        await message.reply(
            reply,
            mention_author=False
        )

    await bot.process_commands(message)

@bot.command(name="snipe")
async def snipe(ctx):

    data = sniped_messages.get(ctx.channel.id)

    if not data:
        await ctx.send("useless ping, no messages to snipe")
        return

    embed = discord.Embed(
        title="Caught YO ass redhanded",
        description=data["content"],
        color=discord.Color.red(),
        timestamp=data["deleted_at"]
    )

    embed.set_author(
        name=data["author_name"],
        icon_url=data["author_avatar"]
    )

    embed.add_field(
        name="Channel",
        value=ctx.channel.mention,
        inline=True
    )

    embed.add_field(
        name="Deleted at",
        value=f"<t:{int(data['deleted_at'].timestamp())}:R>",
        inline=True
    )

    await ctx.send(embed=embed)

bot.run(token)