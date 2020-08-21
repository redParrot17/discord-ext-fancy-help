# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2020 redParrot17

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from discord.ext import commands
from datetime import datetime, timedelta
from discord import utils, Embed, Color

# Needed for the setup.py script
__version__ = '1.0.1-a'

_help_invocations = {}


def _record_invocation(ctx, command):
    """Records when a user invoked help with the specified arguments.

    :param ctx:     context of the command
    :param command: argument string of the help command
    """
    if command is not None:
        tag = f'{ctx.author.id}{command}'
        _help_invocations[tag] = datetime.utcnow()


def _check_invocation(ctx, command):
    """Records when a user invoked help with the specified arguments.

    :param ctx:     context of the command
    :param command: argument string of the help command
    :return:
    """
    if command is not None:
        tag = f'{ctx.author.id}{command}'
        if tag in _help_invocations:
            recent = datetime.utcnow() - timedelta(seconds=15)
            return _help_invocations[tag] >= recent
    return False


def _clean_invocations():
    recent = datetime.utcnow() - timedelta(seconds=15)
    for tag, invoked in _help_invocations.copy().items():
        if invoked < recent:
            del _help_invocations[tag]


class EmbeddedHelpCommand(commands.HelpCommand):
    """The implementation of the embedded help command.

    This inherits from :class:`HelpCommand`.

    It extends it with the following attributes.

    Attributes
    ------------
    color: :class:`discord.Color`
        The color of the help menu's embeds. Defaults to ``Color.blue()``
    dm_help: Optional[:class:`bool`]
        A tribool that indicates if the help command should DM the user instead of
        sending it to the channel it received it from. If the boolean is set to
        ``True``, then all help output is DM'd. If ``False``, none of the help
        output is DM'd. If ``None``, then the bot will only DM when the help
        message becomes too long (dictated by more than 1 embed needed in order to post).
        Defaults to ``False``.
    dm_help_threshold: Optional[:class:`int`]
        The number of embeds that must accumulate before getting DM'd to the
        user if :attr:`dm_help` is set to ``None``. Defaults to 1.
    sort_commands: :class:`bool`
        Whether to sort the commands in the output alphabetically. Defaults to ``False``.
    width: :class:`int`
        The maximum number of characters that fit in a line for category overviews.
        Defaults to 70.
    no_category: :class:`str`
        The string used when there is a command which does not belong to any category(cog).
        Useful for i18n. Defaults to ``"No Category"``
    commands_heading: :class:`str`
        The command list's heading string used when the help command is invoked with a category name.
        Useful for i18n. Defaults to ``"Commands"``
    """

    def __init__(self, **options):
        self.color = options.pop('color', Color.blue())
        self.dm_help = options.pop('dm_help', False)
        self.dm_help_threshold = options.pop('dm_help_threshold', 1)
        self.sort_commands = options.pop('sort_commands', False)
        self.width = options.pop('width', 70)
        self.no_category = options.pop('no_category', 'No Category')
        self.commands_heading = options.pop('commands_heading', 'Commands')

        # Hides the help command itself from the help menu.
        options.update(command_attrs=dict(hidden=True))
        self.embeds = []

        super().__init__(**options)

    @staticmethod
    def shorten_text(text, width):
        """Shortens text to fit into the :param:`width`."""
        if len(text) > width:
            return text[:width - 3] + '...'
        return text

    @staticmethod
    def split_to_max_length(string, length, separator):
        sep_length = len(separator)
        collection_length = 0
        collection = []
        for sub_string in string.split(separator):
            while sub_string:
                sub_sub_string = sub_string[:length]
                sub_sub_string_length = len(sub_sub_string)
                if collection_length + sub_sub_string_length > length:
                    yield ''.join(collection).rstrip(separator)
                    collection_length = 0
                    collection.clear()
                collection_length += sub_sub_string_length
                collection.append(sub_sub_string)
                sub_string = sub_string[length:]
            if collection_length + sep_length > length:
                yield ''.join(collection).rstrip(separator)
                collection_length = 0
                collection.clear()
            else:
                collection_length += sep_length
                collection.append(separator)
        yield ''.join(collection).rstrip(separator)

    def build_embeds(self, title: str, description: str, fields: list):
        """A utility function to put the values into embeds without exceeding embed limits.

        Parameters
        ------------
        title: :class:`str`
            The title of the embed. (Will only be applied to the first embed.)
        description: :class:`str`
            The description of the embed. (Will only be applied to the first embed.)
        fields: :class:`list`
            A list of tuples with the field name as the first value, and the field text as the second value.

        Returns
        -------
        :class:`list`
            List of :class:`discord.Embed` objects containing the data.
        """

        embeds = []
        title = self.shorten_text(title, 256)
        embed = Embed(title=title, color=self.color)

        # Attach the description to the embed.
        descriptions = list(self.split_to_max_length(description, 2048, ' '))
        if len(descriptions) == 1:
            embed.description = descriptions[0]
        elif descriptions:
            for description in descriptions:
                embed.description = description
                embeds.append(embed)
                embed = Embed(color=self.color)

        # Attach the fields to the embed.
        for field_name, field_value in fields:
            field_name = self.shorten_text(field_name, 256)
            field_name_length = len(field_name)
            field_values = self.split_to_max_length(field_value, 1024, '\n')

            for value in field_values:
                field_length = len(value) + field_name_length
                if len(embed.fields) == 25 or len(embed) + field_length > 6000:
                    embeds.append(embed)
                    embed = Embed(color=self.color)
                embed.add_field(name=field_name, value=value, inline=False)

        embeds.append(embed)
        self.embeds = embeds

    async def send_help_menu(self):
        channel = self.get_destination()
        for embed in self.embeds:
            await channel.send(embed=embed)

    def get_destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        elif self.dm_help is None and len(self.embeds) > self.dm_help_threshold:
            return ctx.author
        else:
            return ctx.channel

    async def command_not_found(self, string):
        channel = await self.get_destination()
        if channel is not None:
            string = f'No command called "{string}" found.'
            await channel.send(embed=Embed(color=Color.red(), description=string))

    async def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group):
            return await self.context.send_help(command)
        channel = await self.get_destination()
        if channel is not None:
            string = f'Command "{command.name}" has no sub-commands.'
            await channel.send(embed=Embed(color=Color.red(), description=string))

    async def send_bot_help(self, mapping):
        title = 'Help'
        description = self.context.bot.description
        fields = []

        for cog, cog_commands in mapping.items():
            cog_commands = await self.filter_commands(cog_commands, sort=self.sort_commands)
            if cog_commands:
                cog_name = cog.qualified_name.title() if cog else self.no_category
                cog_value = ', '.join(f'`{c.name}`' for c in cog_commands)
                fields.append((cog_name, cog_value))

        self.build_embeds(title, description, fields)
        await self.send_help_menu()

    async def send_cog_help(self, cog):
        title = f'Help > {cog.qualified_name.title()}'
        description = cog.description
        fields = []

        cog_commands = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        if cog_commands:
            field_name = self.commands_heading
            width = self.width
            lines = []

            for command in cog_commands:
                documentation = command.short_doc.replace('*', '')
                documentation = self.shorten_text(documentation, width)
                line = f'> **{command.name}**\n> {documentation}'.rstrip('\n> ')
                lines.append(line)

            field_value = '\n'.join(lines)
            fields.append((field_name, field_value))

        self.build_embeds(title, description, fields)
        await self.send_help_menu()

    async def send_group_help(self, group):
        parent_name = group.full_parent_name
        group_name = f'{parent_name} {group.name}' if parent_name else group.name
        title = 'Help > ' + ' > '.join(group_name.title().split(' '))
        description = group.help or group.description or group.brief
        fields = []

        group_commands = await self.filter_commands(group.commands, sort=self.sort_commands)
        if group_commands:
            field_name = self.commands_heading
            width = self.width
            lines = []

            for command in group_commands:
                documentation = command.short_doc.replace('*', '')
                documentation = self.shorten_text(documentation, width)
                line = f'> **{command.name}**\n> {documentation}'.rstrip('\n> ')
                lines.append(line)

            field_value = '\n'.join(lines)
            fields.append((field_name, field_value))

        fields.append(('Signature', f'```\n{self.clean_prefix}{group_name} {group.signature}\n```'))
        if group.aliases:
            fields.append(('Aliases', f"```\n{', '.join(group.aliases)}\n```"))

        self.build_embeds(title, description, fields)
        await self.send_help_menu()

    async def send_command_help(self, command):
        parent_name = command.full_parent_name
        command_name = f'{parent_name} {command.name}' if parent_name else command.name
        title = 'Help > ' + ' > '.join(command_name.title().split(' '))
        description = command.help or command.description or command.brief
        fields = [('Signature', f'```\n{self.clean_prefix}{command_name} {command.signature}\n```')]

        if command.aliases:
            fields.append(('Aliases', f"```\n{', '.join(command.aliases)}\n```"))

        self.build_embeds(title, description, fields)
        await self.send_help_menu()

    async def prepare_help_command(self, ctx, command=None):
        """Determines if this command invocation was recently used.

        :param ctx:     command context
        :param command: command string used to invoke help, default None
        :return:        True if similar invocation occurred recently, False otherwise.
        """
        recent = _check_invocation(ctx, command)
        _record_invocation(ctx, command)
        _clean_invocations()
        return recent

    async def command_callback(self, ctx, *, command=None):
        """|coro|

        The actual implementation of the help command.

        - :meth:`send_bot_help`
        - :meth:`send_cog_help`
        - :meth:`send_group_help`
        - :meth:`send_command_help`
        - :meth:`get_destination`
        - :meth:`command_not_found`
        - :meth:`subcommand_not_found`
        - :meth:`send_error_message`
        - :meth:`on_help_command_error`
        - :meth:`prepare_help_command`
        """

        # Check to see if the same invocation was used recently.
        # This handles a situation where a module and command
        # both share the same name.
        recent = await self.prepare_help_command(ctx, command)

        bot = ctx.bot

        # Send the full help command if no command was specified.
        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        # Check for a cog first if similar invocation did not recently occur.
        if not recent:

            # Manually searching instead of a dictionary lookup
            # so as to make the modules case-insensitive.
            lowercase = command.lower()
            for cog_name, cog in bot.cogs.items():
                if cog_name.lower() == lowercase:
                    return await self.send_cog_help(cog)

        maybe_coro = utils.maybe_coroutine

        # If it's not a cog then it's a command.
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.
        keys = command.split(' ')
        cmd = bot.all_commands.get(keys[0])

        # Check for a cog if no command found and we skipped the cog check earlier.
        if cmd is None and recent:

            # Manually searching instead of a dictionary lookup
            # so as to make the modules case-insensitive.
            lowercase = command.lower()
            for cog_name, cog in bot.cogs.items():
                if cog_name.lower() == lowercase:
                    return await self.send_cog_help(cog)

        # Send an error due to the missing command.
        if cmd is None:
            return await maybe_coro(self.command_not_found, self.remove_mentions(keys[0]))

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                return await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
            else:
                if found is None:
                    return await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                cmd = found

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd)
        return await self.send_command_help(cmd)
