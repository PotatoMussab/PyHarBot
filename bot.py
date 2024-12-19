import discord
import time
import os
from discord.ext import tasks, commands
from dotenv import load_dotenv

HARSTEM_SERVER_ID = 382872333167230986
TEST_SERVER_ID = 1319334130021957733
HARSTEM_MOD_ID = 382879493439750144
HARSTEM_OWNER_ID = 382876453089443840
HARSTEM_IDIOT_ID = 877280698824802355
TEST_IDIOT_ID = 1319388713477869568
TEST_MOD_ID = 1319337399431462922
MY_ID = 269107694604910593
IDIOT_CHANNEL_ID = 747578933029109782

#================= Bot class starts here ==================================================

class MyBot(commands.Bot):
    def __init__(this, *args, **kwargs):
        super().__init__(*args,**kwargs)
        this.timedIdiots=[]
        this.testIdiotRole = None
        this.harIdiotRole = None

    async def on_ready(this):
        #print(f'We have logged in as {bot.user}')
        
        async for guild in this.fetch_guilds():
            roleList = await guild.fetch_roles()
            for role in roleList:
                if role.id == TEST_IDIOT_ID:
                    this.testIdiotRole = role
                    break
                if role.id == HARSTEM_IDIOT_ID:
                    this.harIdiotRole = role
                    break
        
    async def setup_hook(this) -> None:
        this.idiotCounter.start()

    async def on_guild_join(guild):
        if guild.id == HARSTEM_SERVER_ID:
            this.harIdiotRole = guild.get_role(HARSTEM_IDIOT_ID)
        if guild.id == TEST_SERVER_ID:
            this.testIdiotRole = guild.get_role(TEST_IDIOT_ID)
    
    async def on_disconnect(this):
        print("Successfully disconnected")
        
    @tasks.loop(minutes=1.0)
    async def idiotCounter(this):
        idiotsToRemove = []
        for i in range(len(this.timedIdiots)):
            currTime = time.time()
            #print(f'Time: {this.timedIdiots[i][1]} Current Time: {time.time()} Is Greater: {currTime > this.timedIdiots[i][1]}')
            if currTime > this.timedIdiots[i][1]:
                if this.timedIdiots[i][2] == HARSTEM_SERVER_ID:
                    await this.timedIdiots[i][0].remove_roles(this.harIdiotRole)
                    #print(f'Unidioted {this.timedIdiots[i][0]} after a timed idiot')
                    idiotsToRemove.append(i)
                if this.timedIdiots[i][2] == TEST_SERVER_ID:
                    await this.timedIdiots[i][0].remove_roles(this.testIdiotRole)
                    #print(f'Unidioted {this.timedIdiots[i][0]} after a timed idiot')
                    idiotsToRemove.append(i)
        for i in idiotsToRemove:
            del this.timedIdiots[i]
            
    @idiotCounter.before_loop
    async def beforeCounting(this):
        await this.wait_until_ready()
        
#=========== Main starts here =================================================================================
intents = discord.Intents.default()
intents.message_content = True
load_dotenv()

bot = MyBot(command_prefix='!', intents=intents)
        
@bot.command()
async def idiot(cntx, *args):
    
    if len(args) == 0: #In case user is not mentioned
        try:
            await cntx.send("Please specify a valid user")
        except:
            channel = cntx.guild.get_channel(IDIOT_CHANNEL_ID)
            await channel.send(f"{targetUser.mention} Idiot!")
        return
    
    
    currGuildId = cntx.guild.id
    
    if currGuildId == HARSTEM_SERVER_ID:
        if cntx.author.get_role(HARSTEM_MOD_ID) == None and cntx.author.get_role(HARSTEM_OWNER_ID) == None:
            return
        
    durationSpecified = False
    numOfIdiots = len(args)
    if args[-1].isnumeric():
        durationSpecified = True
        numOfIdiots -= 1
    for i in range(numOfIdiots):
        converter = commands.MemberConverter()
        targetUser = await converter.convert(cntx, args[i])
        if targetUser.top_role <= cntx.author.top_role:
            try:
                await cntx.send(f"{targetUser.mention} Idiot!")
            except:
                channel = cntx.guild.get_channel(IDIOT_CHANNEL_ID)
                await channel.send(f"{targetUser.mention} Idiot!")
            
            if currGuildId == HARSTEM_SERVER_ID:
                await targetUser.add_roles(bot.harIdiotRole)
            elif currGuildId == TEST_SERVER_ID:
                await targetUser.add_roles(bot.testIdiotRole)
            else:
                return
            if durationSpecified:
                bot.timedIdiots.append((targetUser, time.time() + (float(args[-1]) * 60), cntx.guild.id))
                #print(bot.timedIdiots[0])
                #print(f'Idioted {args[i].mention} for {args[-1]}')
            #else:
                #print(f'Idioted {args[i].mention} indefinitely')
    

@bot.command()
async def unidiot(cntx, *args: discord.Member):
    if len(args) == 0:
        try:
            await cntx.send("Please specify a user")
        except:
            channel = cntx.guild.get_channel(IDIOT_CHANNEL_ID)
            await channel.send(f"{targetUser.mention} Idiot!")
        return
    
    currGuildId = cntx.guild.id
    if currGuildId == HARSTEM_SERVER_ID:
        if cntx.author.get_role(HARSTEM_MOD_ID) == None and cntx.author.get_role(HARSTEM_OWNER_ID) == None:
            return
    for targetUser in args:    
        if cntx.guild.id == HARSTEM_SERVER_ID:
            await targetUser.remove_roles(bot.harIdiotRole)
            #print(f'Unidioted {targetUser.mention} indefinitely')
            return
        if cntx.guild.id == TEST_SERVER_ID:
            await targetUser.remove_roles(bot.testIdiotRole)

@bot.command()
async def exit(cntx):
    
    currGuildId = cntx.guild.id
    if currGuildId == HARSTEM_SERVER_ID:
        if cntx.author.get_role(HARSTEM_MOD_ID) == None and cntx.author.get_role(HARSTEM_OWNER_ID) == None and (not cntx.author.id == MY_ID):
            return
    #print("Disconnecting...")
    await bot.close()

@bot.command()
async def send(cntx, *, message):
    if cntx.guild.id == HARSTEM_SERVER_ID:
        return
    harGuild = bot.get_guild(HARSTEM_SERVER_ID)
    channel = harGuild.get_channel(IDIOT_CHANNEL_ID)
    await channel.send(message)

bot.run(os.getenv('token'))
