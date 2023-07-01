import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext

from functions import inventarize

from config import TOKEN

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot,
                storage=storage)

def get_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Начать новую инвентаризацию'))

    return kb

def get_cancel()-> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отмена'))

class ClientStatesGr(StatesGroup):

    orders = State()
    inventory = State()

@dp.message_handler(commands=['start'])
async def cmd_strt(message: types.Message) -> None:
    await message.answer('Привет, я бот, который поможет тебе провести инвентаризацию.',
                         reply_markup=get_keyboard()
                       )

@dp.message_handler(Text(equals="Отмена", ignore_case=True), state="*")
async def cmd_cncl(message: types.Message, state: FSMContext) -> None:
    await message.reply("Отменил",
                        reply_markup=get_keyboard()
                        )
    await state.finish()

@dp.message_handler(Text(equals="Начать новую инвентаризацию", ignore_case=True), state=None)
async def start_work(message: types.Message) -> None:
    await ClientStatesGr.orders.set()
    await message.answer('Загрузи файл "orders"',
                         reply_markup=get_cancel())

@dp.message_handler(lambda message: not message.document, state=ClientStatesGr.orders)
async def check_doc(message: types.Message):
    return await message.reply('Это не фaйл!')


@dp.message_handler(lambda message: message.document, content_types=types.ContentType.DOCUMENT, state=ClientStatesGr.orders)
async def load_doc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if document := message.document:
            await document.download(
                destination_file=f'orders{message.from_user.id}.xlsx'
            )

        await ClientStatesGr.next()
        await message.reply('А теперь загрузи файл "inventory"')



@dp.message_handler(lambda message: message.document, content_types=types.ContentType.DOCUMENT, state=ClientStatesGr.inventory)
async def load_inventory(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if document := message.document:
            await document.download(
                destination_file=f'inventory{message.from_user.id}.xlsx'
            )

    await message.reply("Файлы загружены и обрабатываются...")

    await bot.send_message(chat_id=message.from_user.id,
                           text=inventarize(inventory=f'./inventory{message.from_user.id}.xlsx', orders=f'./orders{message.from_user.id}.xlsx'),
                           reply_markup=get_keyboard())

    if os.path.isfile(f'./inventory{message.from_user.id}.xlsx'):
        os.remove(f'./inventory{message.from_user.id}.xlsx')
    else:
        pass

    if os.path.isfile(f'./orders{message.from_user.id}.xlsx'):
        os.remove(f'./orders{message.from_user.id}.xlsx')
    else:
        pass

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True)