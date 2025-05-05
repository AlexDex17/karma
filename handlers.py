from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from db import add_user, save_video, update_karma, format_karma_table, get_user_score
from my_queue import add_to_queue, get_next_in_queue, get_video_by_user

router = Router()

# Кнопки для оценки
def get_rating_buttons(sender_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍", callback_data=f"like_{sender_id}"),
         InlineKeyboardButton(text="👎", callback_data=f"dislike_{sender_id}")]
    ])

@router.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user
    add_user(user.id, user.username, user.full_name)
    await message.answer(f"👋 Привет! Отправь видео-кружок, чтобы получить ответ от случайного пользователя.")

@router.message(Command("karma"))
async def karma_handler(message: Message):
    user = message.from_user
    score = get_user_score(user.id)
    await message.answer(f"📊 Ваша карма: {score}")

@router.message(Command("top"))
async def top_handler(message: Message):
    table = format_karma_table()
    await message.answer(table)

@router.message()
async def video_handler(message: Message):
    if message.video_note or message.video:
        user_id = message.from_user.id
        file_id = message.video_note.file_id if message.video_note else message.video.file_id

        partner = get_next_in_queue(user_id)

        if partner:
            try:
                # Отправляем кружок партнёру с кнопками
                await message.bot.send_video_note(partner, file_id)
                await message.bot.send_message(partner, "Как вам это видео?", reply_markup=get_rating_buttons(user_id))

                # Получаем кружок от партнёра и отправляем его нам
                partner_video = get_video_by_user(partner)
                if partner_video:
                    await message.bot.send_video_note(message.chat.id, partner_video)
                    await message.bot.send_message(message.chat.id, "Как вам это видео?", reply_markup=get_rating_buttons(partner))

                await message.answer("✅ Кружок отправлен случайному пользователю.")
            except Exception as e:
                await message.answer("❌ Не удалось обменяться кружком.")
        else:
            add_to_queue(user_id, file_id)
            save_video(user_id, file_id)
            await message.answer("⏳ Ищем вам пару...")

@router.callback_query()
async def rating_handler(callback: CallbackQuery):
    data = callback.data.split("_")
    action, sender_id = data[0], int(data[1])
    voter_id = callback.from_user.id

    if voter_id == sender_id:
        await callback.answer("Вы не можете голосовать за себя.")
        return

    delta = 1 if action == "like" else -1
    update_karma(sender_id, delta)
    await callback.answer("Спасибо за вашу оценку!")
    await callback.message.delete()