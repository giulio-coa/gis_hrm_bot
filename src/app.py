from asyncio import sleep
from logging import INFO, basicConfig, info
from sys import exit

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from dotenv import dotenv_values, find_dotenv

from pyrogram import Client, enums, filters
from pyrogram.handlers import MessageHandler

from uvloop import install

from .plugins import config, manage_jobs, punch, start, update_credentials


if __name__ == '__main__':
    basicConfig(
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s - %(levelname)s - gis-hrm-bot - %(message)s',
        level=INFO
    )

    _config = dotenv_values(
        find_dotenv(raise_error_if_not_found=True, usecwd=True)
    )

    for key in [
        'API_ID',
        'API_HASH',
        'TOKEN',
        'ENDPOINT',
        'USERNAME',
        'PASSWORD',
        'DISABLE_JOBS',
        'MY_ID',
    ]:
        if _config.get(key):
            continue

        exit(f'Missing {key} environment variable.')

    if _config.get('DISABLE_JOBS') not in [
        'true',
        'false',
    ]:
        exit('DISABLE_JOBS environment variable have a wrong value.')

    # If I set the variable to a chat ID, I must convert it to a number
    try:
        _config['MY_ID'] = int(_config.get('MY_ID'))
    except:
        pass

    info('_config: {}'.format(_config))

    install()

    app = Client(
        'gis_hrm_bot',
        api_id=_config.get('API_ID'),
        api_hash=_config.get('API_HASH'),
        bot_token=_config.get('TOKEN'),
        parse_mode=enums.ParseMode.HTML
    )


async def main():
    global app, _config

    async with app:
        # Register handlers
        app.add_handler(
            MessageHandler(
                config,
                filters.chat(_config.get('MY_ID'))
                & filters.incoming
                & filters.private
                & filters.command('config')
            )
        )
        app.add_handler(
            MessageHandler(
                manage_jobs,
                filters.chat(_config.get('MY_ID'))
                & filters.incoming
                & filters.private
                & filters.command('manage_jobs')
            )
        )
        app.add_handler(
            MessageHandler(
                punch,
                filters.chat(_config.get('MY_ID'))
                & filters.incoming
                & filters.private
                & filters.command('punch')
            )
        )
        app.add_handler(
            MessageHandler(
                start,
                filters.chat(_config.get('MY_ID'))
                & filters.incoming
                & filters.private
                & filters.command('start')
            )
        )
        app.add_handler(
            MessageHandler(
                update_credentials,
                filters.chat(_config.get('MY_ID'))
                & filters.incoming
                & filters.private
                & filters.command('update_credentials')
            )
        )

        info('Handler registered.')

        # Register scheduler
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            punch,
            trigger=CronTrigger.from_crontab('0 9,14 * * 1-5'),
            id='punch - in',
            name='punch - in',
            kwargs={
                'client': app,
            }
        )
        scheduler.add_job(
            punch,
            trigger=CronTrigger.from_crontab('0 13,18 * * 1-5'),
            id='punch - off',
            name='punch - off',
            kwargs={
                'client': app,
                'out': True,
            }
        )
        scheduler.start()

        info('Scheduler registered.')

        while True:
            await sleep(1000)


if __name__ == '__main__':
    app.run(main())
