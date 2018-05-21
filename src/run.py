from src.PlumberApp import Plumber

nanoleaf = Plumber('cbartram', 'nanoleaf-layout')
bot = Plumber('cbartram', 'rsps-bot')

nanoleaf.build()
bot.build()

nanoleaf.display()
bot.display()

print(nanoleaf.get_nodes())