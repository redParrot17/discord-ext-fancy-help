# Embedded Help Menu for discord.py Bots
A custom implementation of the default discord.py help menu that uses formatted embeds.

## Customization
This implementation provides several forms of customization to tweak the look of the help menu.

- The color of the embeds.
- If the help menu should be sent in chat or via DMs.
- The maximum number of embeds allowed before defaulting to DMs.
- The maximum width of command documentation to display.
- Whether or not the commands should be sorted alphabetically.
- The category name for commands that don't fall under a Cog.
- The heading to use for group or cog commands.

You can edit these values via the kwargs of the menu's \_\_init\_\_ constructor.
```py
from fancyhelp import EmbeddedHelpCommand
from discord import Color

menu = EmbeddedHelpCommand(
    color=Color.dark_red(),
    sort_commands=True,
    dm_help=None
)
```

## Example

#### As a direct replacement with custom color
```py
from fancyhelp import EmbeddedHelpCommand
from discord.ext.commands import Bot


client = Bot(
    command_prefix='.',
    help_command=EmbeddedHelpCommand(color=0x73D3B3)
)
```

#### As a loadable Cog
```py
from fancyhelp import EmbeddedHelpCommand
from discord.ext.commands import Cog


class Help(Cog):
    """This Cog replaces the default help command with a shiny new one that uses embeds."""

    def __init__(self, bot):
        # We want to preserve the original in case this cog gets unloaded.
        self._original_help_command = bot.help_command

        # Replaces the default help command with our new one.
        bot.help_command = EmbeddedHelpCommand()
        bot.help_command.cog = self
        self.bot = bot

    def cog_unload(self):
        """Restores the default help functionality to the bot."""
        self.bot.help_command = self._original_help_command
        self.bot.help_command.cog = self._original_help_command.cog


def setup(bot):
    bot.add_cog(Help(bot))
```
