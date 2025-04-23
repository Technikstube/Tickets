import discord
from datetime import datetime
from discord.ext import commands
from discord import ui

from utility import Ticket, Config
from view.close import CloseView
from helper.transcript import Transcript

class StartTicketModal(ui.Modal):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            title="Ticket Overview",
            timeout=None,
            custom_id="open_ticket"
        )
        
        self.start = round(datetime.now().timestamp())
        self.bot: commands.Bot = bot
        self.reason = ui.TextInput(
            label="Reason",
            style=discord.TextStyle.short,
            min_length=4,
            max_length=64,
            placeholder="Reason...",
            required=True,
            row=0
        )
        self.first_message = ui.TextInput(
            label="Issue",
            style=discord.TextStyle.paragraph,
            min_length=16,
            max_length=4000,
            placeholder="For a faster Response from our Support-Team, you can already write your issue here.",
            required=True,
            row=1
        )
        
        self.add_item(self.reason)
        self.add_item(self.first_message)
        
    async def on_submit(self, interaction: discord.Interaction):        
        conf = Config().get()
        tickets = Ticket().get()
        
        if str(interaction.user.id) in tickets:
            await interaction.response.send_message("You already have a ticket open.", ephemeral=True, delete_after=3)
            return
        
        category = interaction.guild.get_channel(int(conf["ticket_category"])) if "ticket_category" in conf else None
        staff = interaction.guild.get_role(int(conf["staff_role"])) if "staff_role" in conf else None
        guild = interaction.guild
        user = interaction.user
        
        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        
        standard_overwrite = discord.PermissionOverwrite()
        standard_overwrite.send_messages = True
        standard_overwrite.read_messages = False
        
        if staff is None:
            await interaction.response.send_message("There is no staff-role set, please contact staff.", ephemeral=True)
            return
        
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites={
                user: overwrite,
                staff: overwrite,
                guild.default_role: standard_overwrite
            }
            )
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
            description=f"## :ticket: Ticket by {interaction.user.name} \n**Reason:** {self.reason.value}\n\n",
            colour=discord.Color.lighter_gray())
        
        Transcript(f"configuration/ticket-{interaction.user.name}-{interaction.user.id}.txt").create(interaction.user, self.reason.value, self.first_message.value)
        
        user_embed = discord.Embed(
            title="",
            description=self.first_message.value,
            color=discord.Color.lighter_gray()
        )
        user_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar is not None else interaction.user.default_avatar.url)
        
        await interaction.response.send_message(f"Ticket created {channel.mention}", ephemeral=True, delete_after=15)
        msg = await channel.send(f"<a:loading:1272649967936471202> | {interaction.user.mention}")
        await msg.edit(content=f"{interaction.user.mention}", embed=embed)
        await msg.pin()
        await channel.purge(limit=1)
        await channel.send(embed=user_embed, view=CloseView(self.bot, msg))
    
    def on_timeout(self):
        self.stop()
    
    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message("Something went wrong, try it again later...")
        self.stop()