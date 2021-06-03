import logging
from telethon import TelegramClient, events, Button
from decouple import config
from requests import get
import re

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.INFO
)

bottoken = None
# start the bot
print("Starting...")
apiid = 6
apihash = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
try:
    bottoken = config("BOT_TOKEN")
    api = config("TOR_KEY")
except:
    print("Environment vars are missing! Kindly recheck.")
    print("Bot is quiting...")
    exit()

if bottoken != None:
    try:
        BotzHub = TelegramClient("bot", apiid, apihash).start(bot_token=bottoken)
    except Exception as e:
        print(f"ERROR!\n{str(e)}")
        print("Bot is quiting...")
        exit()
else:
    print("Environment vars are missing! Kindly recheck.")
    print("Bot is quiting...")
    exit()

base_url = "https://api-torrent.vercel.app/api/v1/search?key={api}&query={query}"
detailed_url = "https://api-torrent.vercel.app/api/v1/detail/{id}?key={api}"


@BotzHub.on(events.NewMessage(incoming=True, pattern="^/start"))
async def msgg(event):
    await send_start(event, "msg")


@BotzHub.on(events.callbackquery.CallbackQuery(data="bck"))
async def bk(event):
    await send_start(event, "")


@BotzHub.on(events.callbackquery.CallbackQuery(data="help"))
async def send_help(event):
    await event.edit(
        "**Torrent Searcher.**\n\nSend me a query and I'll search for available magnet links!\nPowered by Torrent API, by @tprojects!\n\nJoin @BotzHub if you liked this bot!",
        buttons=[
            [Button.inline("« Back", data="bck")],
        ],
    )


@BotzHub.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def search_(event):
    if event.raw_text and event.raw_text.startswith("/"):
        return  # ignore commands.
    query = event.raw_text
    a = await event.reply(f"Searching for {query}...")
    await get_results(query, a)


@BotzHub.on(events.callbackquery.CallbackQuery(data=re.compile(b"det_(.*)")))
async def src(event):
    tmp = event.data_match.group(1).decode("UTF-8")
    id, query = tmp.split("|")
    link_ = detailed_url.format(id=id, api=api)
    res_ = get(link_).json()
    msg = """
**Name:** {}
**Category:** {}
**Language:** {}
**Size:** {}
**Added:** {}

**Seeder(s):** {}
**Leecher(s):** {}

**Magnet:** `{}`
""".format(
        res_["name"],
        res_["category"],
        res_["language"],
        res_["size"],
        res_["added"],
        res_["seeder"],
        res_["leecher"],
        res_["magnet"],
    )
    await event.edit(msg, buttons=Button.inline("« Back", data=f"sr_{query}"))


@BotzHub.on(events.callbackquery.CallbackQuery(data=re.compile(b"sr_(.*)")))
async def src(event):
    tmp = event.data_match.group(1).decode("UTF-8")
    await get_results(tmp, event)


# ------------- functions --------------
buttons = [
    [Button.inline("Help", data="help")],
    [
        Button.url("Channel", url="t.me/BotzHub"),
        Button.url("Source", url="https://github.com/xditya/TorrentSearch"),
    ],
]


async def send_start(event, mode):
    user_ = await BotzHub.get_entity(event.sender_id)
    xmsg = f"Hi {user_.first_name}.\n\nI am a Torrent Searcher bot.\nCheck the help for more!"
    if mode == "msg":
        await event.reply(xmsg, buttons=buttons)
    else:
        await event.edit(xmsg, buttons=buttons)


async def get_results(query, a):
    link_ = base_url.format(api=api, query=query)
    res_ = get(link_).json()
    res = res_["result"]
    if len(res) == 0:
        return await a.edit("No results for {}".format(query))
    buts = []
    for i in res:
        try:
            buts.append([Button.inline(i["name"], data=f"det_{i['id']}|{query}")])
        except ValueError:
            pass
    if len(buts) > 100:
        t = buts
        buts = []
        for i in t:
            if not len(buts) > 100:
                buts.append(i)
    return await a.edit(
        "Found {} reults for {}!".format(len(buts), query), buttons=buts
    )


print("Bot has started.")
print("Do visit @BotzHub..")
BotzHub.run_until_disconnected()
