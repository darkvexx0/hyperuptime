import discord
from discord import app_commands
from discord.ext import commands

from .invites import get_invites, change_invites
from .bot_slots import required_invites, can_create_bot
from .storage import load_data, save_data


def register_commands(bot: commands.Bot, owner_id: int):
    @bot.tree.command(name="davet", description="Davet sayını göster")
    async def invite_count(interaction: discord.Interaction):
        count = get_invites(interaction.user.id)
        await interaction.response.send_message(
            f"Geçerli davet sayın: **{count}**",
            ephemeral=True
        )

    @bot.tree.command(name="slot", description="Bot slotu için gereken davetleri göster")
    @app_commands.describe(bot_numarasi="Açmak istediğin bot numarası")
    async def slot(interaction: discord.Interaction, bot_numarasi: app_commands.Range[int, 1, 100]):
        needed = required_invites(bot_numarasi)
        current = get_invites(interaction.user.id)
        allowed = can_create_bot(bot_numarasi, current)

        message = (
            f"**{bot_numarasi}. bot**\n"
            f"Gerekli davet: **{needed}**\n"
            f"Mevcut davet: **{current}**\n"
            f"Durum: **{'Uygun' if allowed else 'Yetersiz davet'}**"
        )
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(name="davetver", description="Bir kullanıcıya davet ekle (Owner)")
    @app_commands.describe(kullanici="Davet verilecek kişi", miktar="Eklenecek davet sayısı")
    async def give_invites(
        interaction: discord.Interaction,
        kullanici: discord.Member,
        miktar: app_commands.Range[int, 1, 100]
    ):
        if interaction.user.id != owner_id:
            await interaction.response.send_message(
                "Bu komutu yalnızca bot sahibi kullanabilir.",
                ephemeral=True
            )
            return

        new_count = change_invites(kullanici.id, miktar)
        await interaction.response.send_message(
            f"{kullanici.mention} kullanıcısına {miktar} davet eklendi. "
            f"Yeni sayı: **{new_count}**"
        )

    @bot.tree.command(name="davetal", description="Bir kullanıcıdan davet sil (Owner)")
    @app_commands.describe(kullanici="Davet alınacak kişi", miktar="Silinecek davet sayısı")
    async def remove_invites(
        interaction: discord.Interaction,
        kullanici: discord.Member,
        miktar: app_commands.Range[int, 1, 100]
    ):
        if interaction.user.id != owner_id:
            await interaction.response.send_message(
                "Bu komutu yalnızca bot sahibi kullanabilir.",
                ephemeral=True
            )
            return

        new_count = change_invites(kullanici.id, -miktar)
        await interaction.response.send_message(
            f"{kullanici.mention} kullanıcısından {miktar} davet silindi. "
            f"Yeni sayı: **{new_count}**"
        )

    @bot.tree.command(name="uptimeekle", description="Uptime takibine URL ekle")
    @app_commands.describe(url="HTTPS web adresi")
    async def add_uptime(interaction: discord.Interaction, url: str):
        if not url.startswith(("https://", "http://")):
            await interaction.response.send_message(
                "Geçerli bir http:// veya https:// adresi gir.",
                ephemeral=True
            )
            return

        data = load_data()
        user_key = str(interaction.user.id)
        urls = data["tracked_urls"].setdefault(user_key, [])

        if url in urls:
            await interaction.response.send_message(
                "Bu adres zaten listende.", ephemeral=True
            )
            return

        urls.append(url)
        save_data(data)
        await interaction.response.send_message(
            f"Uptime listene eklendi: {url}", ephemeral=True
        )