from typing import List
import discord
from discord.ext import commands
from config.constants import PREFIX, TOKEN, MONITOR_CHANNEL_ID, application_id
import os

intents = discord.Intents.all()


class SmallBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            application_id=application_id,
            help_command=None,
        )

    async def setup_hook(self):
        # This loads every python file in directory cogs as an extension.
        for files in os.listdir("./cogs"):
            if files.endswith(".py"):
                await self.load_extension(f"cogs.{files[:-3]}")

    async def on_ready(self):
        print(f"機器人已成功登入為: {self.user}")
        await self.change_presence(activity=discord.Game("監控機器人"))


bot = SmallBot(intents=intents)
emoji_starts_with = ":merak_ball_"


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if not message.content.startswith(emoji_starts_with):
        return
    if not MONITOR_CHANNEL_ID or message.id != MONITOR_CHANNEL_ID:
        return
    # TODO: Add a cache to cache message data for reducing api requests.

    try:
        recent_messages: List[discord.Message] = []
        async for msg in message.channel.history(before=message, limit=10):
            # This is a really bad idea as it makes a lot of http requests, which might make the bot be rate limited.
            if msg.id != message.id:
                recent_messages.append(msg)

        if not recent_messages:
            return  # 沒有歷史訊息跳過

        # 檢查角度差異
        last_valid_msg = None
        for msg in recent_messages:
            if msg.content.startswith(emoji_starts_with):
                last_valid_msg = msg
                break
        if not last_valid_msg:
            return
        last_state = get_state(last_valid_msg)
        current_state = get_state(message)

        diff = abs(last_state - current_state)
        # print(f"當前角度: {deg_int} | 上一角度: {last_deg_int} | 差值: {diff}")
        # If the states' integer representations differs over 2, this is defined as an error.
        if diff > 1:
            await message.reply("錯誤：角度相差超過 30 度！", delete_after=5)
            # await message.delete()
            return

        unique_authors = set()
        for msg in recent_messages:
            if msg.id == last_valid_msg.id:
                break
            if not msg.author.bot:
                unique_authors.add(msg.author.id)

        if len(unique_authors) < 3 and message.author.id in unique_authors:
            await message.reply("錯誤：沒有間隔 3 人！", delete_after=5)
            # await message.delete()
            return

    except (ValueError, IndexError) as e:
        print("錯誤：無法解析角度值！", e)
        return
    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        return


def get_state(msg: discord.Message) -> int:
    """
    Returns which state the emoji is in.
    In theory, the possible return values are integers from 0 to 11 (inclusive).
    """
    try:
        content = msg.content.strip(":")
        parts = content.split("_")
        if len(parts) < 3:
            raise ValueError("訊息格式不正確")
        return int(int(parts[2]) / 30)
        # If parts[2] fails to convert, it will raise ValueError
    except Exception as e:
        raise ValueError(f"無法解析角度值: {e}")


if __name__ == "__main__":
    if not TOKEN:
        print("錯誤：請設定 TOKEN 環境變數")
        exit(1)
    if not MONITOR_CHANNEL_ID:
        print("警告：未設置監控頻道環境變數，這會使on_message的event listener無效")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("登入失敗！檢查 Token 是否正確。")
    except Exception as e:
        print(f"啟動時發生錯誤: {e}")
