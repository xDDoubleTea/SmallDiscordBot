import discord
from discord.ext import commands

# 看要不要用環境變數
TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix='', intents=intents)

@bot.event
async def on_ready():
    print(f"機器人已成功登入為: {bot.user}")
    print(f"機器人 ID: {bot.user.id}")
    print("機器人已準備就緒！")

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    if not message.content.startswith(':merak_ball_'):
        return

    try:
        recent_messages = []
        async for msg in message.channel.history(limit=4):
            if msg.id != message.id:
                recent_messages.append(msg)
        
        if len(recent_messages) < 1:
            return  # 沒有歷史訊息跳過
        
        # 檢查角度差異
        last_valid_msg = None
        for msg in recent_messages:
            if msg.content.startswith(':merak_ball_'):
                last_valid_msg = msg
                break
        
        if last_valid_msg:
            last_deg = get_deg(last_valid_msg)
            current_deg = get_deg(message)
            
            deg_int = int(current_deg)
            last_deg_int = int(last_deg)
            diff = abs(deg_int - last_deg_int)
            # print(f"當前角度: {deg_int} | 上一角度: {last_deg_int} | 差值: {diff}")
            if diff > 30:
                await message.reply("錯誤：角度相差超過 30 度！", delete_after=5)
                await message.delete()
                return
        
        unique_authors = set()
        for msg in recent_messages[:3]:
            if not msg.author.bot:
                unique_authors.add(msg.author.id)
        
        if len(unique_authors) < 3 and message.author.id in unique_authors:
            await message.reply("錯誤：沒有間隔 3 人！", delete_after=5)
            await message.delete()
            return
            
    except (ValueError, IndexError) as e:
        await message.reply("錯誤：無法解析角度值！", delete_after=5)
        await message.delete()
        return
    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        return

def get_deg(msg):
    try:
        content = msg.content.strip(':')
        parts = content.split('_')
        if len(parts) >= 3:
            return parts[2]
        else:
            raise ValueError("訊息格式不正確")
    except Exception as e:
        raise ValueError(f"無法解析角度值: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("錯誤：請設定 DISCORD_TOKEN 環境變數")
        exit(1)
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("登入失敗！檢查 Token 是否正確。")
    except Exception as e:
        print(f"啟動時發生錯誤: {e}")