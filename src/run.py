from src.Plumber import Plumber

nanoleaf = Plumber('cbartram', 'nanoleaf-layout')
bot = Plumber('cbartram', 'rsps-bot')

nanoleaf.build()
nanoleaf.display()
bot.build()

print(nanoleaf.diff(bot.get_root()))
