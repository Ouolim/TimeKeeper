import discord
import pickle
import random
import time
from vars import token, help_message, task_message

client = discord.Client()
adminid = [697140169744187472]


def getid(mention):
    print(mention)
    if mention[:3] == "<@!":
        print("Normální označení")
        return int(mention[3:-1])
    else:
        print("Telefon oznacení")
        return int(mention[2:-1])


def opravneni(func):
    async def g(message):
        if message.author.id not in adminid:
            await say(message, "Nemáš právo!")
        else:
            await func(message)
    return g


async def say(channel, reply):
    await channel.send(reply)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    global active_task, loged, starttime, phase
    print(f"{message.author} wrote: {message.content} in {message.channel}")
    if not message.content.startswith("!") or message.author == client.user:
        return

    if time.time() - starttime > 15 and phase == 'solving':
        print("Uloha deaktivovana po >15 vterinach")
        phase = 'inactive'
        active_task = -1
        loged = []
        for st in us:
            st.correctreply = None
            st.task = -1

    if str(message.author) not in [st.name for st in us] and phase == 'inactive':
        us.append(Student(message))
        save()
        await say(message.channel, f"<@!{message.author.id}> Úspěšně zaregistrováno")

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')
        return 0

    if message.content.startswith('!help'):
        await message.author.send(help_message)
        await message.add_reaction("\N{EYES}")
        return 0

    if message.content.startswith('!tasks'):
        await message.channel.send(task_message)
        return 0

    if message.content.startswith('!start'):
        if phase == "solving":
            await message.channel.send("Pockej chvilku az doresi!")
        if active_task == -1 and phase == "inactive":
            phase = "logging"
            loged = []
            try:
                _, cislo = message.content.split()
                cislo = int(cislo)
            except ValueError:
                await say(message.channel, f"<@!{message.author.id}> Špatně použitý přikaz, musíš napsat !start číslo úlohy")
                return 0
            if cislo > 1:#TODO, aktualne max 1
                await say(message.channel, f"<@!{message.author.id}> Taková úloha zatím neexistuje")
                return 0
            else:
                active_task = cislo
                await say(message.channel, f"!log {cislo}")
        elif phase == "logging":
            phase = "solving"
            starttime = time.time()
            for st in loged:
                await ulohy[active_task](st)

    if message.content.startswith("!log"):
        if active_task == -1:
            await message.channel.send(f"<@!{message.author.id}> Není zapnutá žádná úloha, musíš jí zapnout pomocí !start")
            return 0
        if phase != 'logging':
            await message.channel.send(f"<@!{message.author.id}> Teď není čas na přihlašování, počkej chvíli")
            return 0
        id = [st.name for st in us].index(str(message.author))
        if active_task in us[id].completed:
            await us[id].send(f"<@!{message.author.id}> Tuto úlohu už máš hotovou")
            return 0
        else:
            us[id].task = active_task
            loged.append(us[id])

    if message.content.startswith("!info"):
        try:
            prikaz, ping = message.content.split(" ")
        except ValueError:
            await message.channel.send(f"<@!{message.author.id}> Nesprávný formát zprávy napiš !info a označ hráče, jehož jméno chceš vidět")
            return 0
        try:
            i = [st.id for st in us].index(int(getid(ping)))
        except ValueError:
            await message.channel.send(f"<@!{message.author.id}> Takový uživatel neřeší úlohy")
            return 0
        await message.channel.send(f"<@!{message.author.id}> :robot:<@!{getid(ping)}> má splněno {us[i].completed}")

    if message.content.startswith("!status"):
        await message.channel.send(f"aktivni uloha je {active_task}, prihlaseni jsou {[str(i) for i in loged]}, phase je {phase}, casu ubehlo {time.time()-starttime}")
        return 0

    if message.content.startswith("!solve"):
        answer = message.content[7:]
        id = [st.name for st in us].index(str(message.author))
        if not us[id].correctreply:
            await message.channel.send(f"<@!{message.author.id}> Nejsi aktuálně nikam přihlášený")
            return 0
        print(answer)
        if us[id].correctreply == answer:
            await message.channel.send(f"<@!{message.author.id}> Gratuluji, správná odpověď!")
            us[id].completed.append(active_task)
            us[id].correctreply = None
            us[id].task = 0
            save()
            return 0
        else:
            await message.channel.send(f"<@!{message.author.id}> Bohužel odpověď je špatně! Správně bylo {us[id].correctreply}")
            us[id].correctreply = None
            us[id].task = 0
            return 0


class Student:
    def __init__(self, message):
        self.name = str(message.author)
        self.id = int(message.author.id)
        self.task = -1
        self.completed = []
        self.correctreply = None

    def __str__(self):
        return f"{self.name}"

    async def send(self, message):
        print(self.id)
        u = await client.fetch_user(self.id)
        await u.send(message)


async def uloha0(st):
    a = random.randrange(0,2**15)
    b = random.randrange(0, 2 ** 15)
    st.correctreply = str(a + b)
    await st.send(f"!solve {a} {b}")
    await st.send(st.correctreply)

async def uloha1(st):
    a = [random.randrange(0,2**10) for _ in range(random.randrange(0,2**5))]
    st.correctreply = str(sum(a))
    await st.send(f"!solve {a}".replace("[", "").replace("]","").replace(","," "))
    await st.send(st.correctreply)

def save():
    with open("save.pkl", "wb") as output:
        pickle.dump(us, output, pickle.HIGHEST_PROTOCOL)  # list(Student())


try:
    with open("save.pkl", "rb") as f:  # load data
        us = pickle.load(f)
except BaseException:
    us = []
active_task = -1
loged = []
starttime = -1
phase = "inactive"
ulohy = [uloha0, uloha1]
client.run(token)
