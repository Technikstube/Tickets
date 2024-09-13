import discord
import os
from discord import ui

from utility import Ticket, Config

class YouSureView(ui.View):
    def __init__(self, bot, user_id: int, message: discord.Interaction, reason: str | None=None):
        super().__init__(
            timeout=60
        )
        self.deletebutton = ui.Button(
            style=discord.ButtonStyle.danger,
            row=1,
            label="Ticket löschen",
        )
        self.cancelbutton = ui.Button(
            style=discord.ButtonStyle.gray,
            row=1,
            label="Abbrechen",
        )
        
        self.add_item(self.deletebutton)
        self.add_item(self.cancelbutton)
        
        self.bot = bot
        self.original_message = message
        self.reason = reason
        self.user = user_id
        
        self.deletebutton.callback = self.delete_callback
        self.cancelbutton.callback = self.cancel_callback
        
    async def interaction_check(self, interaction: discord.Interaction):
        if self.user != interaction.user.id:
            await interaction.response.send_message("> :warning: Das ist nicht dein Menü.", ephemeral=True, delete_after=3)
            return False
        return True
        
    async def delete_callback(self, interaction: discord.Interaction):
        self.deletebutton.disabled = True
        self.cancelbutton.disabled = True
        await self.original_message.edit_original_response(content="", view=self)
        
        member = None
        tickets = Ticket().get()
        conf = Config().get()
        transcript = ""
        for ticket in tickets:
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                transcript = Ticket().get()[str(ticket)].get("transcript")
                member = interaction.guild.get_member(int(ticket))
                tickets.pop(ticket)
                break
        Ticket().save(tickets)
        await interaction.channel.delete()
        if member is not None:
            with open(f"configuration/{transcript}", "rb") as f:
                embed = discord.Embed(title="", description=f"Dein Ticket wurde von {interaction.user.mention} geschlossen.", color=discord.Color.blue())
                await member.send(embed=embed, file=discord.File(f))
        if "transcript_channel" in conf:
            tc = self.bot.get_channel(int(conf["transcript_channel"]))
            with open(f"configuration/{transcript}", "rb") as f:
                embed = discord.Embed(title="", description=f"{interaction.channel.name} wurde von {interaction.user.mention} geschlossen.", color=discord.Color.blue())
                await tc.send(embed=embed, file=discord.File(f))
            os.remove(f"./configuration/{transcript}")
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        await self.original_message.delete_original_response()
        await interaction.response.send_message("Vorgang abgebrochen...", ephemeral=True, delete_after=5)
        self.stop()
        
    async def on_timeout(self):
        await self.original_message.delete_original_response()
        self.stop()
        