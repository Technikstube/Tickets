import discord
from datetime import datetime
from discord.ext import commands
from discord import ui

from utility import Ticket, Config
from view.close import CloseView

class StartTicketModal(ui.Modal):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            title="Ticket öffnen",
            timeout=None,
            custom_id="open_ticket"
        )
        
        self.start = round(datetime.now().timestamp())
        self.bot: commands.Bot = bot
        self.reason = ui.TextInput(
            label="Begründung",
            style=discord.TextStyle.short,
            min_length=4,
            max_length=64,
            placeholder="Deine Begründung...",
            required=True,
            row=0
        )
        self.first_message = ui.TextInput(
            label="Nachricht",
            style=discord.TextStyle.paragraph,
            min_length=16,
            max_length=4000,
            placeholder="Zur schnelleren Bearbeitung kannst du hier dein Anliegen bereits beschreiben.",
            required=True,
            row=1
        )
        
        self.add_item(self.reason)
        self.add_item(self.first_message)
        
    async def on_submit(self, interaction: discord.Interaction):        
        conf = Config().get()
        tickets = Ticket().get()
        
        if str(interaction.user.id) in tickets:
            await interaction.response.send_message("Du hast bereits ein Ticket.", ephemeral=True, delete_after=3)
            return
        
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        
        category = self.bot.get_channel(int(conf["ticket_category"]))
        channel = await category.create_text_channel(f"ticket-{interaction.user.name}", overwrites={interaction.user: overwrite})
        await channel.move(beginning=True)
        
        tickets[str(interaction.user.id)] = {
            "channel": channel.id,
            "last_activity": datetime.now().timestamp(),
            "stale": False,
            "transcript": f"ticket-{interaction.user.name}-{interaction.user.id}.txt"
        }
        Ticket().save(tickets)
        
        embed = discord.Embed(
            title="", 
            description=f"## :ticket: Ticket von {interaction.user.name} \n**Begründung:** {self.reason.value}\n\n",
            colour=discord.Color.lighter_gray())
        
        with open(f"configuration/ticket-{interaction.user.name}-{interaction.user.id}.txt", "w", encoding="utf-8") as f:
            date = datetime.now()
            f.write(
                f"# Ticket erstellt am: {date.day}.{date.month}.{date.year}, {date.hour}:{date.minute}:{date.second}\n" \
                f"# Grund: {self.reason.value}\n" \
                f"# von: {interaction.user.name} ({interaction.user.id})\n\n" \
                f"{date.day}.{date.month}.{str(date.year)[2:]}, {date.hour}:{date.minute}:{date.second} | {interaction.user.name}: {self.first_message.value}\n"
            )
        
        user_embed = discord.Embed(
            title="",
            description=self.first_message.value,
            color=discord.Color.lighter_gray()
        )
        user_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar is not None else interaction.user.default_avatar.url)
        
        await interaction.response.send_message(f"Ticket erstellt {channel.mention}", ephemeral=True, delete_after=15)
        msg = await channel.send(f"<a:loading:1272649967936471202> | {interaction.user.mention} <@&1139638391684726884>")
        await msg.edit(content=f"{interaction.user.mention} <@&1139638391684726884>", embed=embed, view=CloseView(self.bot, msg))
        await msg.pin()
        await channel.purge(limit=1)
        await channel.send(embed=user_embed)
    
    def on_timeout(self):
        self.stop()
    
    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message("Etwas ist schiefgelaufen! Versuche es später erneut...")
        self.stop()