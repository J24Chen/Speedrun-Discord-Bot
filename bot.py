import hikari
import lightbulb
import asyncio
from aiohttp import request

bot = lightbulb.BotApp(
    token="MTA1NTY4MjM4Nzc1NDg4OTMwOA.GoABqe.1mc_T7ffKY04iutyEHO3LmuZeermvvY8c7OwJg",
    intents = hikari.Intents.ALL,
    default_enabled_guilds=(839877146243629077)
    )



@bot.listen(hikari.StartedEvent)
async def bot_start(event):
    print("IM ALIVE")


@bot.command
@lightbulb.command("ping","Checks if bot is alive")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    
    await ctx.respond("Pong!")


@bot.command
@lightbulb.option("num1","first number", type=int)
@lightbulb.option("num2","second number", type=int)
@lightbulb.command("add", "adds two numbers together")
@lightbulb.implements(lightbulb.SlashCommand)

async def add(ctx):
    await ctx.respond(ctx.options.num1 + ctx.options.num2)

####
#A simple Animal fact gathered from an API, Uses aiohttp request library
@bot.command
@lightbulb.option("animal","Aminal",type=str)
@lightbulb.command("animalfact", "Gives an Animal fact! (Bird, cat, dog, fox,koala,panda)")
@lightbulb.implements(lightbulb.SlashCommand)

async def fact(ctx):
    animal = ctx.options.animal.lower()
    URL = f"https://some-random-api.ml/animal/{animal}"

    async with request("GET", URL, headers={}) as response:
        if animal in ("dog","cat","bird","fox","koala","panda"):
            if response.status == 200:
                await response.json()   
                data = await response.json()

                #note that json files are treated the same as a python dictionaries USING lists.
                varfact = data["fact"]
                varimg = data["image"]

            ##Sets the respond to an embed, formatted for 
                embed = hikari.Embed(title=f"{animal} fact",
                                    url=URL,
                                    description=varfact)
                if varimg is not None:
                    embed.set_image(varimg)
                
                await ctx.respond(embed)
            else:
                await ctx.respond(f"Pull request failed! response status = {response.status}")
        else:
            await ctx.respond(f"This API does not have info on that animal!")

#################
#ALL apis switch between using dictionaries and lists for their formatting, depending on Curly brackets {} (Dictionaries)
#or normal brackets [] (lists)
#   ################


##### WR bot command, 
# Takes in id and category and returns a video, with time and runner

async def getwr(id,category):
    # id = ctx.options.id.lower()
    
    print(f'id = {id}, category = {category}')
    url2 = f"https://www.speedrun.com/api/v1/leaderboards/{id}/category/{category}"
    async with request("GET",url2, headers={}) as response:
        if response.status == 200:
            data = await response.json()
            info = data["data"]["runs"][0]["run"] #Gets the first place run

            playerid = info["players"][0]["id"]
            playername = await getname(playerid)
            # print (playername)

            time = info["times"]["primary"].strip("PT").lower() #Formats to change "PT1M.095S to 1m0.95s"
            return f'**WR: {time} by {playername}** \n{info["videos"]["links"][0]["uri"]}'
        
        else:
            return f"Pull request failed! response status = {response.status}"



@bot.command
@lightbulb.option("name","Full string game name", type=str)
@lightbulb.command("getwr", "Search a game name and get its wr")
@lightbulb.implements(lightbulb.SlashCommand)

async def getid(ctx):
    name = ctx.options.name.lower()
    url = f"https://www.speedrun.com/api/v1/games?_bulk=yes&name={name}"
    index = 0
    id = None


#Creates a pull request for the API URL
    async with request("GET", url,headers={}) as response:

        if response.status == 200:
            data = await response.json()
            #Grabs the number of titles from the resulting pull request, then prints out the titles.
            titles = len(data["data"])
            if titles > 1:
                titleList = ""
                for i in range(titles):
                    titleList += str(i) + ") " + data["data"][i]["names"]["international"] + "\n"
                await ctx.respond(f"Multiple titles found, choose the right title with the number beside it: \n {titleList}")

            #Waits for the user to input a number, indexing the game they want to choose.
                try: 
                    msg = await bot.wait_for(hikari.GuildMessageCreateEvent,timeout = 60)
                except asyncio.exceptions.TimeoutError:
                    print("user Timeout, did not respond in 60 seconds")
                else:
                    index = int(msg.content)


            elif titles == 1:
                index = 0

            elif titles == 0: 
                await ctx.respond(f'Game Title {name} not found')
                return
                
            try:
                id = data["data"][index]["id"]
            except IndexError:
                await ctx.respond("Error: Number out of range to response.")
                return
            
            #Fetches categories from getCategories, prints a list and waits for user to input a number.
            categoryIndex, categoryList = await getCategories(id)
            await ctx.respond(f'Game ID for {data["data"][index]["names"]["international"]} is {id}\nCategories are \n{categoryList}')
            try: 
                msg2 = await bot.wait_for(hikari.GuildMessageCreateEvent,timeout = 60)
            except asyncio.exceptions.TimeoutError:
                print("user Timeout, did not respond in 60 seconds")
            else:
                category = categoryIndex[int(msg2.content)]["id"]  

            await ctx.respond(await getwr(id,category))
            




#Helper function that returns the name of an id
async def getname(id):
    url = f"https://www.speedrun.com/api/v1/users/{id}"
    
    async with request("GET", url,headers={}) as response:
        if response.status == 200:
            data = await response.json()
            return data["data"]["names"]["international"] 
        

#Helper Function that returns a list of categories 
async def getCategories(id):
    url = f"https://www.speedrun.com/api/v1/games/{id}/categories?"
    categories_formatted = ""

    async with request("GET", url,headers={}) as response:
        if response.status == 200:
            data = await response.json() #Json file returns a dictionary of a list
            for i in range(len(data["data"])):
                categories_formatted += str(i) + ") " + data["data"][i]["name"] + "\n"

    return (data["data"],categories_formatted) #Returns the the category data structure for indexing AND formatted string

bot.run()