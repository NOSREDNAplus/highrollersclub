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
            d["guilds"][g.id] = {"accounts": {"users": {}}, "plots": {}, "stocks": {}, "orginizations": {}, "data": {"jackpot": 0}, "admins": []}
        for u in g.members:
            if u.bot or str(u.id) in d["guilds"][g.id]["accounts"]["users"].copy().keys():
                pass
            else:
                d["guilds"][g.id]["accounts"]["users"][str(u.id)] = {"$": 0, "b$": 0, "cs": 300, "accnum": asyncio.run(genaccnum(16)), "stats": {}, "i": {}, "s": {}, "t": [], "cds": {}, "l": {}} #Money, Banked Money, Credit Score, Account Number, Stats, Subscriptions, Titles, Loans
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
            for c in dict(u["l"]).values():
                c["ts"] += 1
    asyncio.run(update_data(d))
    asyncio.run(log("g", "Cooldown Check Completed!"))
    del d
def intrestcheck():
    d = asyncio.run(get_data())
    for g in dict(d["guilds"]).keys():
        for u in dict(d["guilds"][g]["accounts"]["users"]).values():
            u["b$"] += u["b$"] * 0.02
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
    await statincrease("checkleaderboard", "Clout Checking", ctx)
@client.command()
async def money(ctx:discord.Message, *arg):
    d = await get_data()
    if not "banking" in d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]:
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["banking"] = {"t": 0}
        await update_data(d)
        d = await get_data()
    if arg[0].lower() == "bank":
        if await getcooldown("banking", ctx) == 0:
            d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["banking"]["t"] = 900
            if str(arg[1]).isnumeric():
                if int(arg[1]) <= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]:
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= int(arg[1])
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] += int(arg[1])
                    await update_data(d)
                    await ctx.reply(f"Successfully banked `${arg[1]}`!")
                else:
                    await ctx.reply("Can't bank more than you have!")
            elif arg[1].lower() == "all":
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] += d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]
                await update_data(d)
                await ctx.reply("Successfully banked all your money!")
        else:
            await ctx.reply(f"`{await getcooldown("banking", ctx)}` seconds left until you can bank/unbank again!")
            await statincrease("banking", "Insecure", ctx)
    elif arg[0].lower() == "unbank":
        if await getcooldown("banking", ctx) == 0:
            d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["banking"]["t"] = 900
            if str(arg[1]).isnumeric():
                if int(arg[1]) <= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"]:
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] -= int(arg[1])
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += int(arg[1])
                    await update_data(d)
                    await ctx.reply(f"Successfully un-banked `${arg[1]}`!")
                else:
                    await ctx.reply("Can't un-bank more than you have!")
            elif arg[1].lower() == "all":
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"]
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"] -= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"]
                await update_data(d)
                await ctx.reply("Successfully un-banked all your money!")
        else:
            await ctx.reply(f"`{await getcooldown("banking", ctx)}` seconds left until you can bank/unbank again!")
            await statincrease("banking", "Insecure", ctx)
    elif arg[0].lower() == "round":
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] = round(d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"], 2)
        await update_data(d)
        await ctx.reply(f"Successfully rounded your money to `${d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]}`!")
    elif arg[0].lower() == "give":
        print(arg)
        id = await usernametrans(arg[2], ctx.guild)
        if id != None:
            if str(arg[2]).isnumeric():
                if int(arg[2]) <= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]:
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= int(arg[2])
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] += int(arg[2])
                    await update_data(d)
                    await ctx.reply(f"Successfully gave `${arg[2]}` to {ctx.guild.get_member(int(id)).display_name}!")
                else:
                    await ctx.reply("Can't give more than you have!")
            elif arg[2].lower() == "all":
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] += d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["b$"]
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]
                await update_data(d)
                await ctx.reply(f"Successfully gave all your money to {ctx.guild.get_member(int(id)).display_name}!")
            await statincrease("givemoney", "Philanthropy", ctx)
        else:
            await ctx.reply("This user doesn't exist!")
@client.command()
async def work(ctx: discord.Message):
    d = await get_data()
    if not "work" in d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]:
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["work"] = {"t": 0}
        await update_data(d)
        d = await get_data()
    if await getcooldown("work", ctx) == 0:
        c = random.randint(0, 3)
        sl = ["McDonalds", "Wendys", "Five Guys", "Burger King", "Raising Canes", "Starbucks", "Jimmy Johns", "Arby's"]
        match c:
            case 0:
                i = random.randint(5, 25)
                await ctx.reply(f"You posed as a begger on a street, you gain `${i}`!")
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += i
            case 1:
                i = random.randint(35, 120)
                await ctx.reply(f"You worked at a {random.choice(sl)}, you gain `${i}`!")
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += i
            case 2:
                i = random.randint(45, 80)
                await ctx.reply(f"You worked as a delivery driver, you gain `${i}`!")
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += i
            case 3:
                i = random.randint(25, 50)
                await ctx.reply(f"You mowed some lawns, you gain `${i}`!")
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += i
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["work"]["t"] = 60
        await update_data(d)
        await statincrease("work", "Work Addict", ctx)
    else:
        await ctx.reply(f"`{await getcooldown("work", ctx)}` seconds left until you can work again!")
@client.command()
async def roulette(ctx: discord.Message, arg1: str):
    d = await get_data()
    if arg1.isnumeric():
        if int(arg1) >= 25:
            if int(arg1) <= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"]:
                c1 = random.randint(1, 38)
                if c1 == 1:
                    m = (random.randint(20, 100))/10
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)] * m
                    await ctx.reply(f"## You spin the wheel...\nYou won `${d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)] * m}`!")
                else:
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= int(arg1)
                    await ctx.reply(f"## You spin the wheel...\nYou lost `${arg1}`!")
                await update_data(d)
                await statincrease("gambling", "Avid Gambler", ctx)
            else:
                await ctx.reply("Can't bet more than you have!")
        else:
            await ctx.reply("Can't bet less than `$25`!")
@client.command()
async def slots(ctx: discord.Message):
    d = await get_data()
    if d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] >= 5:
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= 5
        d["guilds"][str(ctx.guild.id)]["data"]["jackpot"] += 5
        c = random.randint(1, 5000)
        if c == 1:
            d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += d["guilds"][str(ctx.guild.id)]["data"]["jackpot"]
            d["guilds"][str(ctx.guild.id)]["data"]["jackpot"] = 0
            await ctx.reply(f"## You spin the slots...\n# :seven::seven::seven:\nYou got the jackpot!... The jackpot is now `${d["guilds"][str(ctx.guild.id)]["data"]["jackpot"]}`")
        else:
            symbols = [":heart:", ":coin:", ":seven:", ":crown:", ":spades:", ":diamonds:", ":joker:"]
            o = []
            while len(o) != 3:
                o.append(random.choice(symbols))
            await ctx.reply(f"## You spin the slots...\n# {o[0]}{o[1]}{o[2]}\nSadly you don't get a jackpot... The jackpot is now `${d["guilds"][str(ctx.guild.id)]["data"]["jackpot"]}`")
        await update_data(d)
        await statincrease("gambling", "Avid Gambler", ctx)
    else:
        await ctx.reply("You don't have enough money!")
@client.command()
async def rob(ctx: discord.Message, arg1):
    d = await get_data()
    id = await usernametrans(arg1, ctx.guild)
    #if you're dumb enough to rob yourself do it
    if not "rob" in d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]:
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["rob"] = {"t": 0}
        await update_data(d)
        d = await get_data()
    if id != None:
        if await getcooldown("rob", ctx) == 0:
            if d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] > 0:
                c = random.randint(1, 20)
                dn = ctx.guild.get_member_named(arg1).display_name
                if c == 1:
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["rob"]["t"] = 900
                    p = random.randint(5, 9)
                    await ctx.reply(f"## You try to rob {dn}...\nAnd you succede, you gain `${round(d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] * float(f"0.0{p}"), 2)}`!")
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += round(d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] * float(f"0.0{p}"), 2)
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] -= round(d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] * float(f"0.0{p}"), 2)
                    await statincrease("robbing", "Robin Hood", ctx)
                else:
                    await ctx.reply(f"## You try to rob {dn}...\nAnd you fail, you're fined `$500`!")
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= 500
                    await statincrease("notrobbing", "A Bad Pickpocket", ctx)
                await update_data(d)
            else:
                await ctx.reply("You can't rob someone you're broke!")
        else:
            await ctx.reply(f"`{await getcooldown("rob", ctx)}` seconds left until you can rob someone again!")
    else:
        await ctx.reply("This user doesn't exist!")
@client.command()
async def bank(ctx: discord.Message, *arg):
    d = await get_data()
    print(arg)
    if not "loaning" in d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]:
        d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["loaning"] = {"t": 0}
        await update_data(d)
        d = await get_data()
    if arg[0].lower() == "loan":
        if str(arg[1]).isnumeric():
            if await getcooldown("loaning", ctx) == 0:
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cds"]["loaning"]["t"] = 3600
                ud = await get_data(); ud = ud["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]
                #<579 = 10,000, <669 = 100,000, <739 = 500,000,<799 = 1,000,000, <850 = 2,000,000
                maxl = None
                cs = ud["cs"]
                if cs < 579:
                    maxl = 10000
                elif cs < 669:
                    maxl = 100000
                elif cs < 739:
                    maxl = 500000
                elif cs < 799:
                    maxl = 1000000
                elif cs < 850:
                    maxl = 2000000
                else:
                    maxl = 0
                if int(arg[1]) <= maxl:
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"][len(d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"])+1] = {"ts": 0, "a": int(arg[1]), "o": round(int(arg[1]) + int(arg[1]) * 0.05)}
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] += int(arg[1])
                    await ctx.reply(f"Successfully loaned `${arg[1]}`!")
                    await update_data(d)
                else:
                    await ctx.reply(f"You can't loan more than `${maxl}`!")
            else:
                await ctx.reply(f"`{await getcooldown("loaning", ctx)}` seconds left until you can loan money!")
                await statincrease("loaning", "Loan Shark?", ctx)
        elif str(arg[1]).lower() == "payback" and str(arg[2]).isnumeric() and str(arg[3]).isnumeric():
            if int(arg[2]) <= (len(d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"])):
                if int(arg[3]) < d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"][str(arg[2])]["o"] :
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"][str(arg[2])]["o"] -= int(arg[3])
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= int(arg[3])
                    await ctx.reply(f"Successfully payed back `${arg[3]}` on loan `{int(arg[2])}`!")                
                elif int(arg[3]) >= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"][str(arg[2])]["o"] :
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["$"] -= d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"][str(arg[2])]["o"]
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["cs"] += 5
                    #add scaling credit score increase
                    await ctx.reply(f"Successfully payed back `${d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"][str(arg[2])]["o"]}` on loan `{arg[2]}`!")
                    d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]["l"].pop(str(arg[2]))
                await update_data(d)
            else:
                await ctx.reply("You don't have this loan!")
    elif arg[0].lower() == "loans":
        ud = d["guilds"][str(ctx.guild.id)]["accounts"]["users"][str(ctx.author.id)]
        if len(ud["l"]) != 0:
            ll = []
            for i in ud["l"].items():
                ll.append((i[1]["ts"], i[1]["a"], i[0], i[1]["o"])) #time since, amount
            pl = []
            for i in ll:
                pl.append(f"{i[2]}. **Owed**: `${i[3]}` **Loaned**:`${i[1]}` - `{i[0]}` seconds ago")
            await ctx.reply(f"## Your Loans\n{'\n'.join(pl)}")
        else:
            await ctx.reply(f"## Your Loans\n-# non-existent...")
@client.command(name="?")
async def help(ctx: discord.Message):
    d = await get_data()
    await ctx.reply("## Commmands\n- `$profile`: <optional: user> - Tells you information about this user's account!\n- `$stats` - Tells you how many times you've done certain actions\n- `$money`: <required: bank | unbank | round | give> <req: amount | 'all'> - Allows you to bank and unbank your money\n- `$work` - Make a random amount of money by working an odd job\n- `$slots` - Roll the slots, increase the jackpot or win it!\n- `$roulette` <required: amount> - Spin the wheel and double or more your bet!\n- `$rob` <required: user> - Rob someone or get fined (oh no!)!\n- `$suggest`: <required: suggestion> <IN PROGRESS>")
    if ctx.author.id in d["guilds"][str(ctx.guild.id)]["admins"] or ctx.author.id == ctx.guild.owner_id or ctx.author.id in d["developers"]:
        await ctx.reply("## Admin Commands\n- `$give-money`: <required: user> <required: amount>\n- `$clear-cooldowns`: <required: user>\n- `$add-admin`: <required: user>\n- `$remove-admin`: <required: user>\n- `$annoy`: <required: user> <required: times> <optional: message>\n- `$set-money`: <required: user> <required: amount>")
#admin commands
@client.command(name="give-money")
async def givemoney(ctx: discord.Message, arg1, arg2):
    d = await get_data()
    id = await usernametrans(arg1, ctx.guild)
    if ctx.author.id in d["guilds"][str(ctx.guild.id)]["admins"] or ctx.author.id == ctx.guild.owner_id or ctx.author.id in d["developers"]:
        if id != None:
            if str(arg2).isnumeric():
                arg2 = int(arg2)
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] += arg2
                await ctx.reply(f"Successfully added `${arg2}` to {arg1}'s account")
                await update_data(d)
        else:
            await ctx.reply("This user doesn't exist!")
    else:
        await ctx.reply("You have to be an admin, server owner, or a developer to use this command!")

@client.command(name="set-money")
async def setmoney(ctx: discord.Message, arg1, arg2):
    d = await get_data()
    id = await usernametrans(arg1, ctx.guild)
    if ctx.author.id in d["guilds"][str(ctx.guild.id)]["admins"] or ctx.author.id == ctx.guild.owner_id or ctx.author.id in d["developers"]:
        if id != None:
            if str(arg2).isnumeric():
                arg2 = int(arg2)
                d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["$"] = arg2
                await ctx.reply(f"Successfully set {arg1}'s account to `${arg2}`")
                await update_data(d)
        else:
            await ctx.reply("This user doesn't exist!")
    else:
        await ctx.reply("You have to be an admin, server owner, or a developer to use this command!")

@client.command("clear-cooldowns")
async def clearcooldowns(ctx: discord.Message, arg1):
    d = await get_data()
    id = await usernametrans(arg1, ctx.guild)
    if ctx.author.id in d["guilds"][str(ctx.guild.id)]["admins"] or ctx.author.id == ctx.guild.owner_id or ctx.author.id in d["developers"]:
        if id != None:
            for i in d["guilds"][str(ctx.guild.id)]["accounts"]["users"][id]["cds"].values():
                print(i)
                i["t"] = 0
            await update_data(d)
            await ctx.reply(f"Successfully cleared cooldowns for {arg1}")
        else:
            await ctx.reply("This user doesn't exist!")
    else:
        await ctx.reply("You have to be an admin, server owner, or a developer to use this command!")
@client.command("add-admin")
async def addadmin(ctx: discord.Message, arg1):
    d = await get_data()
    id = await usernametrans(arg1, ctx.guild)
    if str(ctx.author.id) in d["guilds"][str(ctx.guild.id)]["admins"] or ctx.author.id == ctx.guild.owner_id or ctx.author.id in d["developers"]:
        if id != None:
            d["guilds"][str(ctx.guild.id)]["admins"].append(int(id))
            await update_data(d)
            await ctx.reply(f"Successfully added {arg1} as an admin!")
        else:
            await ctx.reply("This user doesn't exist!")
    else:
        await ctx.reply("You have to be an admin, server owner, or a developer to use this command!")
@client.command(name="annoy")
async def annoy(ctx: discord.Message, *arg):
    d = await get_data()
    print(arg)
    id = await usernametrans(arg[0], ctx.guild)
    if ctx.author.id in d["guilds"][str(ctx.guild.id)]["admins"] or ctx.author.id == ctx.guild.owner_id or ctx.author.id in d["developers"]:
        if id != None:
            if arg[1].isnumeric():
                if int(arg[1]) <= 5:
                    msg = "hii :)"
                    print(len(arg))
                    if len(arg) == 3:
                        msg = arg[2]
                    for _ in range(int(arg[1])):
                        await ctx.reply(f"{ctx.guild.get_member(int(id)).mention} {msg}"); sleep(0.1)
                else:
                    await ctx.reply("You Can't Annoy Someone More Than 5 Times At Once")
            else:
                await ctx.reply("Your Annoy Rate Has To Be A Number You Idiot")

        else:
            await ctx.reply("This user doesn't exist!")
    else:
        await ctx.reply("You have to be an admin, server owner, or a developer to use this command!")
@client.command("remove-admin")
async def removeadmin(ctx: discord.Message, arg1):
    d = await get_data()
    id = await usernametrans(arg1, ctx.guild)
    if ctx.author.id in d["guilds"][str(ctx.guild.id)]["admins"] or ctx.author.id == ctx.guild.owner_id or ctx.author.id in d["developers"]:
        if id != None:
            d["guilds"][str(ctx.guild.id)]["admins"].remove(int(id))
            await update_data(d)
            await ctx.reply(f"Successfully removed {arg1} as an admin!")
        else:
            await ctx.reply("This user doesn't exist!")
    else:
        await ctx.reply("You have to be an admin, server owner, or a developer to use this command!")
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Gambling"))
with open('config.json', 'r') as f:
    d = json.load(f)
    t = threading.Thread(target=mainloop, daemon= True); t.start()
    client.run(d["token"])
    del d
