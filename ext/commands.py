import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands

from utility import Ticket, Config
from view.yousure import YouSureView
from view.start_ticket import StartTicketView

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    settings = app_commands.Group(name="settings", description="All Ticket-Settings in one place.", guild_only=True)

    @app_commands.command(name="close", description="Close a Ticket")
    @commands.guild_only()
    @app_commands.default_permissions(manage_nicknames=True)
    async def close_command(self, interaction: discord.Interaction, reason: Optional[str]):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                embed = discord.Embed(title="Delete Ticket?", description="Are you sure you want to delete this ticket?", color=discord.Color.red())
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(self.bot, interaction.user.id, interaction, reason), ephemeral=True)
                return

        await interaction.response.send_message("This channel is not a ticket.", ephemeral=True, delete_after=3)

    @app_commands.command(name="send_ticket_message", description="Send the Ticket Message")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def send_message_command(self, interaction: discord.Interaction):
        
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="",
            description="Click on **`Open Ticket`** to open a ticket!"
        )
        embed.set_author(name="Open a Ticket", icon_url=self.bot.user.avatar.url)
        
        await interaction.channel.send(embed=embed, view=StartTicketView(self.bot))
        await interaction.response.send_message("Message created!", ephemeral=True, delete_after=5)

    @settings.command(name="staff_role", description="Set the Staff Role")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def staff_role_command(self, interaction: discord.Interaction, role: discord.Role):
        conf = Config().get()
        
        if role.id == conf["staff_role"]:
            await interaction.response.send_message("The Staff Role is not removable", ephemeral=True)
            return
        
        if not isinstance(role, discord.Role):
            await interaction.response.send_message("Given ID is not a role.", ephemeral=True)
            return
        
        conf["staff_role"] = role.id
        Config().save(conf)
        
        await interaction.response.send_message(f"Staff-Role is now {role.mention}.", ephemeral=True)

    @settings.command(name="category", description="Set the Ticket-Category")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def category_command(self, interaction: discord.Interaction, category_id: str):
        conf = Config().get()
        
        _chn = self.bot.get_channel(int(category_id))
        
        if not isinstance(_chn, discord.CategoryChannel):
            await interaction.response.send_message("Given ID is not category.", ephemeral=True)
        
        conf["ticket_category"] = category_id
        Config().save(conf)
        
        await interaction.response.send_message(f"Ticket-Category is now `{_chn.name}`.", ephemeral=True)

    @settings.command(name="transcripts", description="Set the Transcripts-Channel")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def transcript_command(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conf = Config().get()
        
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("Given ID is not a text channel.", ephemeral=True)
        
        conf["transcript_channel"] = channel.id
        Config().save(conf)
        
        await interaction.response.send_message(f"Transcript-Channel is now {channel.mention}.", ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(Commands(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    print(f"> {__name__} unloaded")