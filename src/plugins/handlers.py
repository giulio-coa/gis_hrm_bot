from datetime import datetime
from os import environ
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
async def clean_messages(_, message: Message) -> None:
    await message.delete(revoke=True)


async def manage_jobs(_, message: Message) -> None:
    if len(message.command) != 2:
        await message.reply_text(
            'The <em>/manage_jobs</em> command accepts a single parameter indicating the punch status.<br>Allowed values ​​are: <em>enable</em> and <em>disable</em>.'
        )
        return

    value = {
        'disable': 'false',
        'enable': 'true',
    }.get(message.command[1])

    if not value:
        await message.reply_text(
            'The <em>/manage_jobs</em> command accepts a single parameter indicating the punch status.<br>Allowed values ​​are: <em>enable</em> and <em>disable</em>.'
        )
        return

    await set_env_vars(message, 'DISABLE_JOBS', value)


async def punch(client: Client, message: Message, out: bool = False) -> None:
    config = {
        **environ,
        **dotenv_values(
            find_dotenv(raise_error_if_not_found=True, usecwd=True)
        ),
    }

    # If I set the variable to a chat ID, I must convert it to a number
    try:
        config['MY_ID'] = int(config.get('MY_ID'))
    except:
        pass

    if message:
        if len(message.command) != 2:
            await message.reply_text(
                'The <em>/punch</em> command accepts a single parameter indicating the punch status.<br>Allowed values ​​are: <em>out</em> (or <em>off</em> or <em>0</em>) and <em>in</em> (or <em>on</em> or <em>1</em>).'
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
            raise BadRequest(
                'The <em>/punch</em> command accepts a single parameter indicating the punch status.<br>Allowed values ​​are: <em>out</em> (or <em>off</em> or <em>0</em>) and <em>in</em> (or <em>on</em> or <em>1</em>)s.'
            )
            return
    # If I'm here, is a scheduled job
    # I want exit if is an holiday or if I have disabled the jobs
    elif datetime.now().date() in Italy(years=datetime.now().year).keys() or config.get('DISABLE_JOBS', True) == 'true':
        return

    # try:
    #     api = GIS_HRM_API(
    #         config.get('ENDPOINT'),
    #         config.get('USERNAME'),
    #         config.get('PASSWORD')
    #     )

    #     api.punch(out)
    # except Exception as e:
    #     await message.reply_text(f'Exception: {e}')

    if not message:
        await client.send_message(
            chat_id=config.get('MY_ID'),
            text=f'out: {out}'
        )
        await client.send_message(
            chat_id=config.get('MY_ID'),
            text='<strong>Scheduled action.</strong><br><em>Command:</em> <code>/punch {}</code><br><em>Result:</em> Done.'.format(
                'out' if out else 'in'
            )
        )
        return

    await message.reply_text(f'out: {out}')
    await message.reply_text('Done.')


async def start(_, message: Message) -> None:
    await message.reply_text(
        '⁠',
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
            'The <em>/update_credentials</em> command accepts two parameters indicating what do you want update and its value.<br>You want update a variable that I don\'t support.'
        )
        return

    await set_env_vars(message, key, message.command[2])
