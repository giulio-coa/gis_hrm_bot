from datetime import datetime
from logging import info
from typing import Any

from dotenv import dotenv_values, find_dotenv, set_key

from holidays import Italy

from pyrogram import Client
from pyrogram.types import Message, ReplyKeyboardMarkup

from ..libraries import GIS_HRM_API


#########
# Tools #
#########
async def set_env_vars(message: Message, key: str, value: Any) -> None:
    res, _, _ = set_key(
        find_dotenv(raise_error_if_not_found=True, usecwd=True),
        key,
        f'"{value}"',
        quote_mode='never'
    )

    if not res:
        await message.reply_text('Failed.')
        return

    await message.reply_text('Done.')


############
# Handlers #
############
async def manage_jobs(_, message: Message) -> None:
    info('Received message:\n{}'.format(message))

    if len(message.command) != 2:
        await message.reply_text(
            'The <em>/manage_jobs</em> command accepts a single parameter indicating the punch status.\nAllowed values ​​are: <em>enable</em> and <em>disable</em>.'
        )
        return

    value = {
        'disable': 'false',
        'enable': 'true',
    }.get(message.command[1])

    if not value:
        await message.reply_text(
            'The <em>/manage_jobs</em> command accepts a single parameter indicating the punch status.\nAllowed values ​​are: <em>enable</em> and <em>disable</em>.'
        )
        return

    await set_env_vars(message, 'DISABLE_JOBS', value)


async def punch(client: Client, message: Message = None, out: bool = False) -> None:
    if message:
        info('Received message:\n{}'.format(message))
    else:
        info('Client:\n{}'.format(client))
        info('Message:\n{}'.format(message))
        info('out: {}'.format(out))

    config = dotenv_values(
        find_dotenv(raise_error_if_not_found=True, usecwd=True)
    )

    info('config: {}'.format(config))

    # If I set the variable to a chat ID, I must convert it to a number
    try:
        config['MY_ID'] = int(config.get('MY_ID'))
    except:
        pass

    if message:
        if len(message.command) != 2:
            await message.reply_text(
                'The <em>/punch</em> command accepts a single parameter indicating the punch status.\nAllowed values ​​are: <em>out</em> (or <em>off</em> or <em>0</em>) and <em>in</em> (or <em>on</em> or <em>1</em>).'
            )
            return

        out = {
            'out': True,
            'off': True,
            '0': True,

            'in': False,
            'on': False,
            '1': False,
        }.get(message.command[1])

        if out is None:
            await message.reply_text(
                'The <em>/punch</em> command accepts a single parameter indicating the punch status.\nAllowed values ​​are: <em>out</em> (or <em>off</em> or <em>0</em>) and <em>in</em> (or <em>on</em> or <em>1</em>)s.'
            )
            return
    # If I'm here, is a scheduled job
    # I want exit if is an holiday
    elif datetime.now().date() in Italy(years=datetime.now().year).keys():
        info('Skip because is a holiday.')
        return
    # If I'm here, is a scheduled job
    # I want exit if I have disabled the jobs
    elif config.get('DISABLE_JOBS', 'true') == 'true':
        info('Skip because the jobs are disabled.')
        return

    try:
        api = GIS_HRM_API(
            config.get('ENDPOINT'),
            config.get('USERNAME'),
            config.get('PASSWORD')
        )

        api.punch(out)

        del api
    except Exception as e:
        if not message:
            await client.send_message(
                chat_id=config.get('MY_ID'),
                text='<strong>Scheduled action.</strong>\n<em>Command:</em> <code>/punch {}</code>\n<em>Result:</em> Failed.\n<em>Exception:</em> {}'.format(
                    'out' if out else 'in',
                    e
                )
            )
            return

        await message.reply_text(f'Exception: {e}')
        return

    if not message:
        await client.send_message(
            chat_id=config.get('MY_ID'),
            text='<strong>Scheduled action.</strong>\n<em>Command:</em> <code>/punch {}</code>\n<em>Result:</em> Done.'.format(
                'out' if out else 'in'
            )
        )
        return

    await message.reply_text('Done.')


async def start(_, message: Message) -> None:
    info('Received message:\n{}'.format(message))

    await message.reply_text(
        'Hello {},\nThe following keyboard will help you to send the main commands.'.format(
            f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
            or f'@{message.from_user.username}',
        ),
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    '/punch in',
                ],
                [
                    '/punch out',
                ],
            ],
            is_persistent=True,
            resize_keyboard=True
        )
    )


async def update_credentials(_, message: Message) -> None:
    info('Received message:\n{}'.format(message))

    if len(message.command) != 3:
        await message.reply_text(
            'The <em>/update_credentials</em> command accepts two parameters indicating what do you want update and its value.'
        )
        return

    key = {
        'username': 'USERNAME',
        'password': 'PASSWORD',
    }.get(message.command[1])

    if not key:
        await message.reply_text(
            'The <em>/update_credentials</em> command accepts two parameters indicating what do you want update and its value.\nYou want update a variable that I don\'t support.'
        )
        return

    await set_env_vars(message, key, message.command[2])

    await message.delete(revoke=True)
