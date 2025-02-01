import threading, json, discord, asyncio, string, random
from time import sleep
from discord.ext import commands

intents = discord.Intents.all()

client = commands.Bot(command_prefix='$', intents=intents)

tlog = []
async def log(type: str, text: str) -> None:
    if type == None:
        type = "g"
    """
    Type = WARN(w), ERROR(e), GENERAL(g)
    
    Logs information to the console.
    """
    type = type.lower()
    match type:
        case "w":
            print(f"[WARN] {text}")
            tlog.append(f"[WARN] {text}")
        case "e":
            print(f"[ERROR] {text}")
            tlog.append(f"[ERROR] {text}")
        case "g":
            print(f"[GENERAL] {text}")
            tlog.append(f"[GENERAL] {text}")
async def get_data() -> dict:
    """
    Gets dictionary of config in config.json
    """
    with open("config.json", "r") as f:
        d = json.load(f)
        f.close()
    del f
    return d
async def update_data(d:dict) -> None:
    """
    Buffers updates for 'config.json'
    """
    with open("config.json", "w") as f:
        json.dump(d, f, indent=6)
        f.close()
    del f
async def genaccnum(l:int):
    c, p = 0, ""
    while c != l:
        p = p + random.choice(string.ascii_letters)
        c +=1
    return p
async def usernametrans(t:str, g: discord.guild.Guild) -> str | None:
    a = None
    t = str(t)
    for i in g.members:
        if i.mention == t or str(i.id) == t or i.name == t or i.global_name == t or i.display_name == t:
            a = str(i.id)
    return a
async def statincrease(sn:str, dn:str, ctx:discord.Message, i:int = 1) -> None:
    d = await get_data()
    us = d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["s"]
    if not sn in dict(us).keys():
        us[sn] = {"td":0, "dn": dn} #times done
    us[sn]["td"] += i
    await update_data(d)
async def getcooldown(cn:str, ctx:discord.Message):
    d = await get_data()
    return d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"][cn]["t"]
def usercheck():
    d = asyncio.run(get_data())
    for g in client.guilds:
        g.id = str(g.id)
        if not g.id in d["guilds"].copy().keys():
            d["guilds"][g.id] = {"accounts": {"bots": {}, "users": {}}, "plots": {}, "stocks": {}, "orginizations": {}}
        for u in g.members:
            if u.bot or str(u.id) in d["guilds"][g.id]["accounts"]["users"].copy().keys():
                pass
            else:
                d["guilds"][g.id]["accounts"]["users"][str(u.id)] = {"$": 0, "b$": 0, "cs": 300, "accnum": asyncio.run(genaccnum(16)), "stats": {}, "i": {}, "s": {}, "t": [], "cds": {}} #Money, Banked Money, Credit Score, Account Number, Stats, Subscriptions, Titles
    asyncio.run(update_data(d))
    asyncio.run(log("g", "User Check Completed!"))
    del d
def cdcheck():
    d = asyncio.run(get_data())
    for g in dict(d["guilds"]).keys():
        for u in dict(d["guilds"][g]["accounts"]["users"]).values():
            for c in dict(u["cds"]).values():
                if c["t"] > 0:
                    c["t"] -= 1
    asyncio.run(update_data(d))
    asyncio.run(log("g", "Cooldown Check Completed!"))
    del d
def intrestcheck():
    d = asyncio.run(get_data())
    for g in dict(d["guilds"]).keys():
        for u in dict(d["guilds"][g]["accounts"]["users"]).values():
            u["b$"] += u["b$"] * 0.002
    asyncio.run(update_data(d))
    asyncio.run(log("g", "Intrest add Completed!"))
def mainloop():
    o = 0
    while True:
        usercheck()
        cdcheck()
        if o >= 900:
            intrestcheck()
            o = 0
        sleep(1)
        o +=1
class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Button",style=discord.ButtonStyle.gray)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.edit_message(content=f"This is an edited button response!")
#commands
@client.command()
async def profile(ctx: discord.Message, *arg):
    if len(arg) == 0:
        ud = await get_data(); ud = ud["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]
        if len(ud["t"]) == 0:
            await ctx.reply(f"## {ctx.author.display_name}\n**$**: `{ud["$"]}`\n**Banked $**: `{ud["b$"]}`\n**Credit Score**: `{ud["cs"]}`")
        else:
            await ctx.reply(f"## {ctx.author.display_name}\n-# {", ".join(ud["t"])}\n\n**$**: `{ud["$"]}`\n**Banked $**: `{ud["b$"]}`\n**Credit Score**: `{ud["cs"]}`")
    else:
        if await usernametrans(arg[0], ctx.guild) == None:
            await ctx.reply("This user doesn't exist!")
        else:
            id = await usernametrans(arg[0], ctx.guild)
            ud = await get_data(); ud = ud["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]
            if len(ud["t"]) == 0:
                await ctx.reply(f"## {ctx.guild.get_member(int(id)).display_name}\n**$**: `{ud["$"]}`\n**Credit Score**: `{ud["cs"]}`")
            else:
                await ctx.reply(f"## {ctx.guild.get_member(int(id)).display_name}\n-# {", ".join(ud["t"])}\n\n**$**: `{ud["$"]}`\n**Credit Score**: `{ud["cs"]}`")
            await statincrease("checkuserprofile", "Checked User's Profile", ctx)
@client.command()
async def stats(ctx: discord.Message):
    ud = await get_data(); ud = ud["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]
    if len(ud["s"]) == 0:
        await ctx.reply(f"## {ctx.author.display_name}'s Stats\n-# none")
    else:
        pl = []
        for i in dict(ud["s"]).values():
            print(i)
            pl.append(f"- **{i["dn"]}**: `{i["td"]}`")
        await ctx.reply(f"## {ctx.author.display_name}'s Stats\n{"\n".join(pl)}")
@client.command()
async def leaderboard(ctx: discord.Message):
    d = await get_data()
    usd = d["guilds"][str(ctx.guild.id)]["accounts"]["users"]
    nl = []
    for i in usd.items():
        nl.append((ctx.guild.get_member(int(i[0])), i[1]["$"] + i[1]["b$"]))
    if len(nl)-1 < 4:
        r = 5 - (len(nl)-1)
        itr = 0
        while r != itr:
            nl.append(("None", 0))
            itr += 1
    t = sorted(nl, key = lambda x: x[1], reverse= True)
    await ctx.reply(f"## Leaderboard\n- **{t[0][0]}**: `${t[0][1]}`\n- **{t[1][0]}**: `${t[1][1]}`\n- **{t[2][0]}**: `${t[2][1]}`\n- **{t[3][0]}**: `${t[3][1]}`\n- **{t[4][0]}**: `${t[4][1]}`")  
@client.command()
async def money(ctx:discord.Message, *arg):
    d = await get_data()
    if arg[0].lower() == "bank":
        if str(arg[1]).isnumeric():
            if int(arg[1]) <= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]:
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= int(arg[1])
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] += int(arg[1])
                await update_data(d)
                await ctx.reply(f"Successfully banked ${arg[1]}!")
            else:
                await ctx.reply("Can't bank more than you have!")
        elif arg[1].lower() == "all":
            d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] += d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]
            d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]
            await update_data(d)
            await ctx.reply("Successfully banked all your money!")
    elif arg[0].lower() == "unbank":
        if str(arg[1]).isnumeric():
            if int(arg[1]) <= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"]:
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] -= int(arg[1])
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += int(arg[1])
                await update_data(d)
                await ctx.reply(f"Successfully un-banked ${arg[1]}!")
            else:
                await ctx.reply("Can't un-bank more than you have!")
        elif arg[1].lower() == "all":
            d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"]
            d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] -= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"]
            await update_data(d)
            await ctx.reply("Successfully un-banked all your money!")
    elif arg[0].lower() == "round":
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] = round(d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"], 2)
        await update_data(d)
        await ctx.reply(f"Successfully rounded your money to ${d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]}!")
@client.command()
async def work(ctx: discord.Message):
    d = await get_data()
    if not "work" in d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]:
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["work"] = {"t": 0}
        await update_data(d)
        d = await get_data()
    if await getcooldown("work", ctx) == 0:
        c = random.randint(0, 2)
        sl = ["McDonalds", "Wendys", "Five Guys", "Burger King", "Raising Canes", "Starbucks"]
        match c:
            case 0:
                i = random.randint(5, 25)
                await ctx.reply(f"You posed as a begger on a street, you gain ${i}!")
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += i
            case 1:
                i = random.randint(35, 120)
                await ctx.reply(f"You worked at a {random.choice(sl)}, you gain ${i}!")
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += i
            case 2:
                i = random.randint(45, 80)
                await ctx.reply(f"You worked as a delivery driver, you gain ${i}!")
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += i
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["work"]["t"] = 60
        await update_data(d)
    else:
        await ctx.reply(f"`{await getcooldown("work", ctx)}` seconds left until you can work again!")
@client.command()
async def roulette(ctx: discord.Message, arg1: str):
    d = await get_data()
    if arg1.isnumeric():
        if int(arg1) <= 25:
            if int(arg1) <= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]:
                c1 = random.randint(1, 38)
                if c1 == 1:
                    m = (random.randint(20, 100))/20
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)] * m
                    await ctx.reply(f"## You spin the wheel...\nYou won `${d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)] * m}`!")
                else:
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= int(arg1)
                    await ctx.reply(f"## You spin the wheel...\nYou lost `${arg1}`!")
                await update_data(d)
            else:
                await ctx.reply("Can't bet more than you have!")
        else:
            await ctx.reply("Can't bet less than `$25`!")
@client.command()
async def blackjack(ctx: discord.Message):
    await ctx.reply("Hello World!", view=Buttons())
@client.command(name="?")
async def help(ctx: discord.Message):
    await ctx.reply("## Commmands\n- `$profile`: <optional: user> - Tells you information about this user's account!\n- `$stats` - Tells you how many times you've done certain actions\n- `$money`: <required: bank | unbank | round> <req: amount | 'all'> - Allows you to bank and unbank your money\n- `$work` - Make a random amount of money by working an odd job")
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Gambling"))
with open('config.json', 'r') as f:
    d = json.load(f)
    t = threading.Thread(target=mainloop, daemon= True); t.start()
    client.run(d["token"])
    del d