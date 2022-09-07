from keep_alive import keep_alive
import discord
import math
from discord.ext import commands
from gsheet import *
from marketAnalysis import *
import datetime

client = commands.Bot(command_prefix = '!', case_insensitive=True)

@client.event
async def on_ready():
    print('Bot is ready')
    
@client.event
async def on_message(message):
    if(message.content.lower().startswith('swing investment idea')):
        addInvestmentCall(message.content)    
    elif(message.content.lower().startswith('swing investment update')):
        updateInvestmentCall(message.content)
    elif(message.content.lower().startswith('positional investment idea')):
        addPositionalCall(message.content)
    elif(message.content.lower().startswith('positional investment update')):
        updatePositionalCall(message.content)
    await client.process_commands(message)
    

@client.command()
async def hello(self):
    await self.send("Hi")
  
@client.command()
async def display(ctx, *arguments):
    if(len(arguments)==3):
        status, itype = arguments[:2]
        time = ''
    elif(len(arguments)==5):
        status, itype = arguments[:2]
        time = arguments[-1]
    else:
        await ctx.send("Invalid query. Please use below format:\n>>> !display Open Swing calls \n !display Open Swing calls for oct \n !display Closed swing calls \n !display Closed swing calls for month \n !display All swing calls for oct \n !display All swing calls \n !display Open positional calls \n !display Open positional calls for oct \n !display Closed positional calls \n !display Closed positional calls for month \n !display All positional calls for oct \n !display All positional calls ")
        
    if(itype.lower() == 'swing'):
        df = displayData(itype, status, time)
        stream = df2imgs(df)
        stream.seek(0)
        chart = discord.File(stream,filename="unemployment_chart.png")
        await ctx.send(file=chart)
    elif(itype.lower() == 'positional'):
        df = displayData(itype, status, time)
        stream = df2imgs(df)
        stream.seek(0)
        chart = discord.File(stream,filename="unemployment_chart.png")
        await ctx.send(file=chart)
    else:
        await ctx.send("Invalid query. Please use below format:\n>>> !display Open Swing calls \n !display Open Swing calls for oct \n !display Closed swing calls \n !display Closed swing calls for month \n !display All swing calls for oct \n !display All swing calls \n !display Open positional calls \n !display Open positional calls for oct \n !display Closed positional calls \n !display Closed positional calls for month \n !display All positional calls for oct \n !display All positional calls ")
    
  


@client.command()
async def targetSetting(ctx):
    def check(msg):
        return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id
    
    pS = discord.Embed(title='Welcome to Target Setting by Money Monitors',
                       description='Please enter the following for target recommendation',
                       color = 0x00ff00)
    pS.add_field(name = 'Enter **StockName**, **CMP**, **SL** and **Risk:Reward**.', value = 'Ex: IRCTC, 6000, 5700, 1:2', inline=True)
    await ctx.send(embed=pS)
    answermsg = await client.wait_for('message', check = check)

    try:
        stock, cmp, sl, rr = map(lambda x: x.strip(), answermsg.content.split(','))
        target = round(float(rr.split(':')[1])*(float(cmp)-float(sl))+float(cmp),2)
        qE = discord.Embed(title=stock,
                           description='Following are the trade components:',
                           color = 0x008080)
        qE.add_field(name='CMP: ', value=cmp, inline=True)
        qE.add_field(name='StopLoss: ', value=sl, inline=True)
        qE.add_field(name='MinTarget: ', value=target, inline=True)
        qE.add_field(name='Risk:Reward: ', value=rr, inline=True)
        qE.set_footer(text='Good trade if min target is achieved')
        await ctx.send(embed=qE)
        await ctx.send('Thanks for using me!\nWish you good luck with your trade')
        
    except Exception as E:
        await ctx.send(">>> Please Enter the correct format.\nStockName, BookPrice, StopLoss, RiskAppetite\nEx: IRCTC, 6000, 5700, 20000")




@client.command()
async def positionSizing(ctx):
    def check(msg):
        return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id
    
    pS = discord.Embed(title='Welcome to Position Sizing by Money Monitors',
                       description='Please choose from the following:',
                       color = 0x00ff00)
    pS.add_field(name = '1. Identify **Quantity**', value = 'Identify Quantity based on cmp, SL and Risk', inline=False)
    pS.add_field(name = '2. Identify **Risk**', value='Identify Risk based on cmp, SL and Quantity', inline=False)
    pS.add_field(name = '3. Identify **SL**', value='Identify SL based on cmp, Quantity and Risk', inline=True)
    await ctx.send(embed=pS)
    answermsg = await client.wait_for('message', check = check)
    if "1" in answermsg.content.lower():
        runLoop = True
        while(runLoop):
            await ctx.send("Enter **StockName**, **CMP**, **SL** and **Risk**\nEx: IRCTC, 6000, 5700, 20000")
            answermsg2 = await client.wait_for('message', check = check)
            #reponse = answermsg2.content
            try:
                stock, cmp, sl, risk = map(lambda x: x.strip(), answermsg2.content.split(','))
                q = math.floor(float(float(risk)/float((float(cmp)-float(sl)))))
                target = round(2*(float(cmp)-float(sl))+float(cmp),2)
                qE = discord.Embed(title=stock,
                                   description='Following are the trade components:',
                                   color = 0x008080)
                qE.add_field(name='CMP: ', value=cmp, inline=True)
                qE.add_field(name='StopLoss: ', value=sl, inline=True)
                qE.add_field(name='Quantity: ', value=q, inline=True)
                qE.add_field(name='Risk: ', value=risk, inline=True)
                qE.add_field(name='MinTarget: ', value=target, inline=True)
                qE.add_field(name='Risk:Reward: ', value='1:2', inline=True)
                qE.set_footer(text='Good trade if min target is achieved')
                await ctx.send(embed=qE)
                await ctx.send('Want to continue?? (Yes/No)')
                ans = await client.wait_for('message', check = check)
                if(ans.content.lower()=='no' or ans.content.lower()!='yes'):
                    runLoop = False
                    await ctx.send('Thanks for using me!\nWish you good luck with your trade')
                  
            except Exception as E:
                await ctx.send(">>> Please Enter the correct format.\nStockName, BookPrice, StopLoss, RiskAppetite\nEx: IRCTC, 6000, 5700, 20000")
            
    elif "2" in answermsg.content.lower():
#        await ctx.send("Enter StockName, CMP, SL and Quantity(IRCTC, 6000, 5700, 20):")
        runLoop = True
        while(runLoop):
            await ctx.send("Enter **StockName**, **CMP**, **SL** and **Quantity**\nEx: IRCTC, 6000, 5700, 66")
            answermsg2 = await client.wait_for('message', check = check)
            #reponse = answermsg2.content
            try:
                stock, cmp, sl, q = map(lambda x: x.strip(), answermsg2.content.split(','))
                risk = round((float(q)*float(cmp))-(float(q)*float(sl)),2)
                target = round(2*(float(cmp)-float(sl))+float(cmp),2)
                qE = discord.Embed(title=stock,
                                   description='Following are the trade components:',
                                   color = 0x008080)
                qE.add_field(name='CMP: ', value=cmp, inline=True)
                qE.add_field(name='StopLoss: ', value=sl, inline=True)
                qE.add_field(name='Quantity: ', value=q, inline=True)
                qE.add_field(name='Risk: ', value=risk, inline=True)
                qE.add_field(name='MinTarget: ', value=target, inline=True)
                qE.add_field(name='Risk:Reward: ', value='1:2', inline=True)
                qE.set_footer(text='Good trade if min target is achieved')
                await ctx.send(embed=qE)
                await ctx.send('Want to continue?? (Yes/No)')
                ans = await client.wait_for('message', check = check)
                if(ans.content.lower()=='no' or ans.content.lower()!='yes'):
                    runLoop = False
                    await ctx.send('Thanks for using me!\nWish you good luck with your trade')
                  
            except Exception as E:
                await ctx.send(">>> Please Enter the correct format.\nStockName, BookPrice, StopLoss, RiskAppetite\nEx: IRCTC, 6000, 5700, 20000")
    elif "3" in answermsg.content.lower():
        runLoop = True
        while(runLoop):
            await ctx.send("Enter **StockName**, **CMP**, **Quantity** and **Risk**\nEx: IRCTC, 6000, 66, 20000")
            answermsg2 = await client.wait_for('message', check = check)
            #reponse = answermsg2.content
            try:
                stock, cmp, q, risk = map(lambda x: x.strip(), answermsg2.content.split(','))
                sl = round(((float(q)*float(cmp))-float(risk))/float(q),2)
                target = round(2*(float(cmp)-float(sl))+float(cmp),2)
                qE = discord.Embed(title=stock,
                                   description='Following are the trade components:',
                                   color = 0x008080)
                qE.add_field(name='CMP: ', value=cmp, inline=True)
                qE.add_field(name='StopLoss: ', value=sl, inline=True)
                qE.add_field(name='Quantity: ', value=q, inline=True)
                qE.add_field(name='Risk: ', value=risk, inline=True)
                qE.add_field(name='MinTarget: ', value=target, inline=True)
                qE.add_field(name='Risk:Reward: ', value='1:2', inline=True)
                qE.set_footer(text='Good trade if min target is achieved')
                await ctx.send(embed=qE)
                await ctx.send('Want to continue?? (Yes/No)')
                ans = await client.wait_for('message', check = check)
                if(ans.content.lower()=='no' or ans.content.lower()!='yes'):
                    runLoop = False
                    await ctx.send('Thanks for using me!\nWish you good luck with your trade')
                  
            except Exception as E:
                await ctx.send(">>> Please Enter the correct format.\nStockName, BookPrice, StopLoss, RiskAppetite\nEx: IRCTC, 6000, 5700, 20000")

    else:
        await ctx.send("Invalid response")


@client.command()
#the content will contain the question, which must be answerable with yes or no in order to make sense
async def pollYN(ctx, *, content:str):
  print("Creating yes/no poll...")
  #create the embed file
  embed=discord.Embed(title=f"{content}", description="React to this message with ✅ for yes, ❌ for no.",  color=0xd10a07)
  #set the author and icon
  embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url) 
  print("Embed created")
  #send the embed 
  message = await ctx.channel.send(embed=embed)
  #add the reactions
  await message.add_reaction("✅")
  await message.add_reaction("❌")


@client.command()
async def dailyAnalysis(ctx, *arguments):
        
    df = dailyMarketAnalysis()
    for name, streams in df.items(): 
        print(name,streams)       
        streams.seek(0)
        chart = discord.File(streams,filename="unemployment_chart.png")
        await ctx.send(file=chart)
    





keep_alive()
client.run("ODk5NjYwMTEwNTU5ODM4Mjc4.YW1_xQ.DCIoflQp4VZVawSNBCtuUUQGkJc")
