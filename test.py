import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import random
import html

TOKEN = "7202020971:AAFiAub1-5gtAWpnVqjDflduDoASNOnm2dI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Сохраняем правильный ответ в контексте пользователя
user_correct_answers = {}

# Функция для очистки текста от HTML-спецсимволов
def format_text(text: str) -> str:
    return html.unescape(text)  # Декодирует &quot; -> ", &amp; -> &, и т. д.

# Функция для получения вопросов из API
def get_question():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    response = requests.get(url).json()
    question_data = response['results'][0]

    question = format_text(question_data['question'])  # Форматируем вопрос
    correct_answer = format_text(question_data['correct_answer'])  # Форматируем правильный ответ
    incorrect_answers = [format_text(ans) for ans in question_data['incorrect_answers']]  # Форматируем варианты

    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)  # Перемешиваем ответы

    return {
        "question": question,
        "correct_answer": correct_answer,
        "all_answers": all_answers
    }

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я викторина-бот. Напиши /quiz, чтобы начать.")

# Обработчик команды /quiz
@dp.message(Command("quiz"))
async def quiz(message: types.Message):
    # Получаем вопрос
    question_data = get_question()

    question = question_data['question']
    all_answers = question_data['all_answers']
    correct_answer = question_data['correct_answer']

    # Сохраняем правильный ответ для текущего пользователя
    user_correct_answers[message.from_user.id] = correct_answer

    # Создаем кнопки
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=answer)] for answer in all_answers],
        resize_keyboard=True
    )

    # Отправляем вопрос с клавиатурой
    await message.answer(f"🎮 **{question}**", parse_mode="Markdown", reply_markup=keyboard)

# Обработчик текстовых сообщений (ответов на викторину)
@dp.message()
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    user_answer = message.text

    if user_id in user_correct_answers:
        correct_answer = user_correct_answers[user_id]
        del user_correct_answers[user_id]  # Удаляем правильный ответ после проверки

        if user_answer == correct_answer:
            await message.answer("✅ Правильно!", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer(f"❌ Неправильно! Правильный ответ: {correct_answer}",
                                 reply_markup=types.ReplyKeyboardRemove())

        # Предлагаем новую викторину
        await message.answer("Напиши /quiz для нового вопроса.")
    else:
        # Если пользователь отправил сообщение не в ответ на викторину
        await message.answer("Чтобы начать викторину, напиши /quiz.")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())