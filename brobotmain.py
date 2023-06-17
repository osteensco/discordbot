import os
import time
from websearch import GoogleSearch
from chat import AIChat
import discord
from dotenv import load_dotenv





load_dotenv('token.env')
TOKEN = os.environ.get('DISCORD_TOKEN')
SERVER = os.environ.get('DISCORD_CHANNEL')
DEFAULT_CHANNEL = os.environ.get('DEFAULT_CHANNEL')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
server = client.get_guild(SERVER)


# command functions
async def search_google(txt, message):
    '''
    Searches google using the entire text following the command, returns the first 5 results.
    '''
    await message.channel.send(message.author.mention)
    results = API['google'].search(txt)
    return results

async def generate_link(txt, message):
    '''
    Creates an invite link that does not expire.
    '''
    link = await message.channel.create_invite(max_age=0)
    return f"""Here ya go: {link}"""

async def retrain_AIChat(txt, message):
    '''
    Executes the AIChat train_model() method. Only the owner of brobot can use this command.
    '''
    admin_role =  message.guild.get_role(1003377962978123827)
    if admin_role in message.author.roles:
        status = discord.Activity(type=discord.ActivityType.listening, name='The Spirit Consults')
        await client.change_presence(activity=status)
        API['chat'].train_model()
        time.sleep(5)
        await client.change_presence(activity=None)
    else:
        return f'''yea, no, I'm good thanks.'''
    return '''Man, what a trip...'''




API = {
    'chat': AIChat(),
    'google': GoogleSearch()
}



commands = {
    'google': search_google,
    'link': generate_link,
    'retrain': retrain_AIChat,
}

async def display_commands(txt, message):
    '''
    Lists all currently available commands.
    '''
    commmands_list = 'I can execute the following commands: \n'
    for cmd in commands.keys():
        commmands_list += f'''\n!{cmd}: {commands[cmd].__doc__}'''
    
    return commmands_list

commands['help'] = display_commands



async def execute_command(cmd, txt, message):
    command = commands[cmd]
    response = await command(txt, message)
    if response:
        if isinstance(response, list):
            for result in response:
                await message.channel.send(result)
        else:
            await message.channel.send(response)






# event listeners
@client.event
async def on_ready():
    await client.wait_until_ready()
    channel = client.get_channel(int(DEFAULT_CHANNEL))
    await channel.send("""I'm back bitches""")

@client.event
async def on_message(message):

    if str(message.author) != 'brobot#8118':
        reply = API['chat'].chat(message.content)
        if reply:
            await message.channel.send(reply)

        index = message.content.find('!')
        if index != -1:
            try:
                end_index = message.content.index(' ', index) 
                txt = message.content[end_index+1:]
            except ValueError:
                end_index = len(message.content)
                txt = ''

            cmd = message.content[index+1:end_index]
            await message.channel.send("beep boop")
            if cmd in commands:
               await execute_command(cmd, txt, message)
            else:
                await message.channel.send(f'''sorry, "{cmd}" is not a command that I have, for a list of valid commands use !help''')










if __name__ == '__main__':

    client.run(TOKEN)


