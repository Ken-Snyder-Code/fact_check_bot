import discord
from discord.ext import commands, tasks
import os
import gpt_api
import fact_check_api
import asyncio

async def get_fact_check(comment, message):
    response = gpt_api.analyze_disc_comment(comment)

    print(response)

    if response != None:
        #on message, bot will react with the magnifying glass emoji
        await message.add_reaction('🔍')

        if response['Verdict'] == 'False':

            #change emoji to ⚠️ 
            await message.add_reaction('⚠️')
            await message.clear_reaction('🔍')
            

            fact_check_links = fact_check_api.get_fact_check_response(response['Keywords'])


            if len(fact_check_links) == 0:
                fact_check_links = None
            fact_check_response = gpt_api.create_fact_check_response(comment, response['Verdict'], response['Explanation'], fact_check_links)

            os.system('cls')

            return (fact_check_response)
        if response['Verdict'] == 'True':

            #change emoji to ✔️ 
            await message.add_reaction('✔️')
            await message.clear_reaction('🔍')
            
        #await bot.process_commands(message)  # Allow commands to be processed

            return None
        if response['Verdict'] == 'Not Making a Claim':

            await message.clear_reaction('🔍')
            return None

    else:
        return None

def main(): 
    # Read the token from
    with open(r'C:\Code\Python\Discord\fact_check_bot\token.txt') as file:
        token = file.read()

    print(token)

    # Set up the bot with intents
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    #Store the channel that the bot is monitoring
    monitored_channel = set()

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')

    @bot.command(name='fact_check')
    async def fact_check(ctx):
            await ctx.send("I am now watching this chat. I will monitor comments and provide fact checking when necessary.")
            # Add the current channel to the monitored channels
            monitored_channel.add(ctx.channel.id)

    @bot.event
    async def on_message(message):
        #ignore messages sent by the bot itself
        if message.author == bot.user:
            return

        # Check if the channel is being monitored
        if message.channel.id in monitored_channel:

            #Capture the comment
            comment = message.content


            #run the async function to get the fact check
            task = get_fact_check(comment, message)
            fact_check = await task
            if fact_check is not None:
                await message.channel.send(fact_check)





        #This is necessary for !fact_check to still work
        await bot.process_commands(message)


    #run the bot
    bot.run(token)

if __name__ == "__main__":
    main()


    ''' comments may need to have tripple quotes so it can handle single qutotes and stuff like that.'''