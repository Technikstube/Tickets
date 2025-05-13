import discord
import pytz
from datetime import datetime

MESSAGE = "{} | {}{}: {}\n"

class Transcript:
    
    def __init__(self, file_path: str):
        self.file_path = file_path

    @staticmethod
    def _get_time() -> str:
        _timezone = pytz.timezone("Europe/Berlin")
        _date = datetime.now()
        return _date.strftime("%d.%m.%Y, %H:%M:%S")
    
    def create(self, user: discord.User, reason: str, message: str):
        date = self._get_time()
        
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(
                f"# Ticket created on: {date}\n" \
                f"# Reason: {reason}\n" \
                f"# by: {user.name} ({user.id})\n\n" \
                f"{MESSAGE.format(date, "", user.name, message)}"
            )

    def append(self, user: discord.User, message: str):
        date = self._get_time()
        
        with open(self.file_path, "a", encoding="UTF-8") as file:
            file.write(
                MESSAGE.format(date, "", user.name, message)
            )
            
    def append_edited(self, user: discord.User, old: str, new: str):
        date = self._get_time()
        
        with open(self.file_path, "a", encoding="UTF-8") as file:
            file.write(
                MESSAGE.format(date, "[Edited/OLD] ", user.name, old)
            )
            file.write(
                MESSAGE.format(date, "[Edited/NEW] ", user.name, new)
            )
            
    def append_as_system(self, message: str):
        date = self._get_time()
        
        with open(self.file_path, "a", encoding="UTF-8") as file:
            file.write(
                MESSAGE.format(date, "", "System", message)
            )
    