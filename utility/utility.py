import json

config = "configuration/configuration.json"
tickets = "configuration/tickets.json"

class Config:
    def __init__(self):
        pass
    
    def get(self) -> dict:
        with open(config, "r") as cf:
            data = json.load(cf)
        return data

    def save(self, conf: dict) -> None:
        with open(config, "w") as cf:
            json.dump(conf, cf, indent=4)

class Ticket:
    def __init__(self):
        pass
    
    def get(self) -> dict:
        with open(tickets, "r") as tf:
            data = json.load(tf)
        return data
    
    def get_ticket(self, user_id: int) -> dict | None:
        with open(tickets, "r") as tf:
            data = json.load(tf)
        return data[str(user_id)] if str(user_id) in data else None

    def get_ticket_channel_id(self, user_id: int) -> int | None:
        with open(tickets, "r") as tf:
            data = json.load(tf)
        return data[str(user_id)]["channel"] if str(user_id) in data else None     

    def save(self, ticket: dict) -> None:
        with open(tickets, "w") as tf:
            json.dump(ticket, tf, indent=4)