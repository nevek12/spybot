import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from handlers import other, user, game
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from rediskey.keyredis import KeyRedis

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)

# Выводим в консоль информацию о начале запуска бота
logger.info('Starting bot')

# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    key_red = KeyRedis()
    redis = Redis(host='localhost', port=6379, db=0)
    storage = RedisStorage(redis=redis, key_builder=key_red)

    dp = Dispatcher(storage=storage)

    # Настраиваем главное меню бота
    # await set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.include_router(user.user_router)
    dp.include_router(game.game_router)
    dp.include_router(other.other_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())