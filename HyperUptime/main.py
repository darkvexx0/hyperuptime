import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks

from modules.commands import register_commands
from modules.storage import load_data, save_data
from modules.uptime import check_url

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
PORT = int(os.getenv("PORT", "10000"))

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN ortam değişkeni ayarlanmamış.")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def health(request):
    return web.Response(text="Hyper Uptime is running.")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()


@tasks.loop(seconds=180)
async def uptime_loop():
    data = load_data()
    all_urls = {
        url
        for urls in data["tracked_urls"].values()
        for url in urls
    }

    for url in all_urls:
        result = await check_url(bot.http_session, url) if hasattr(bot, "http_session") else None
        if result:
            print(result)


@bot.event
async def on_ready():
    print(f"Giriş yapıldı: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi.")
    except Exception as error:
        print(f"Komut senkronizasyon hatası: {error}")

    if not uptime_loop.is_running():
        uptime_loop.start()


@bot.event
async def on_member_join(member: discord.Member):
    data = load_data()

    try:
        invites = await member.guild.invites()
    except discord.Forbidden:
        print("Davet takibi için Manage Server izni gerekiyor.")
        return

    current = {invite.code: invite.uses for invite in invites}
    previous = data["invite_uses"].get(str(member.guild.id), {})

    used_code = next(
        (code for code, uses in current.items()
         if uses > previous.get(code, 0)),
        None
    )

    data["invite_uses"][str(member.guild.id)] = current

    if used_code:
        invite = next((i for i in invites if i.code == used_code), None)
        if invite and invite.inviter and invite.inviter.id != member.id:
            from modules.invites import is_account_old_enough, change_invites

            if is_account_old_enough(member.created_at):
                inviter_id = str(invite.inviter.id)
                data["invites"][inviter_id] = (
                    int(data["invites"].get(inviter_id, 0)) + 1
                )
                data["invite_uses"][str(member.guild.id)] = current
                save_data(data)
            else:
                print(f"{member} hesabı 21 günden yeni; davet sayılmadı.")

    save_data(data)


@bot.event
async def on_member_remove(member: discord.Member):
    # Ayrılan üyenin davet sahibini doğru belirlemek için
    # davet kullanım geçmişi ve üye-atıf kaydı tutulmalıdır.
    data = load_data()
    attribution = data.setdefault("invite_attribution", {})
    inviter_id = attribution.pop(str(member.id), None)

    if inviter_id:
        from modules.invites import change_invites
        change_invites(int(inviter_id), -1)

    save_data(data)


async def main():
    register_commands(bot, OWNER_ID)
    await start_web_server()
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())