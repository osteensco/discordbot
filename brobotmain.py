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
    API['google'].search(txt)

async def generate_link(txt, message):
    link = await message.channel.create_invite(max_age=0)
    return f"""Here ya go: {link}"""

async def retrain_AIChat(txt, message):
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
    commmands_list = 'I can execute the following commands: '
    for cmd in commands.keys():
        commmands_list += f'''\n!{cmd}'''
    
    return commmands_list

commands['help'] = display_commands




@client.event
async def on_ready():
    await client.wait_until_ready()
    channel = client.get_channel(int(DEFAULT_CHANNEL))
    await channel.send("""I'm back bitches""")

@client.event
async def on_message(message):

    if str(message.author) != 'brobot#8118':
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
               response = await commands[cmd](txt, message)
               if response:
                await message.channel.send(response)
            else:
                await message.channel.send(f'''sorry, "{cmd}" is not a command that I have, for a list of valid commands use !help''')
        
        if "lol" in message.content:
            await message.channel.send(f"""yes, {message.author.display_name}... humor.""")

        if client.user.mentioned_in(message):
            reply = API['chat'].chat(message.content)
            await message.channel.send(reply)










if __name__ == '__main__':

    client.run(TOKEN)


