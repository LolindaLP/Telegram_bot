import asyncio
import requests
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import random
import html

TOKEN = "7202020971:AAFiAub1-5gtAWpnVqjDflduDoASNOnm2dI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь для хранения вопросов пользователей
user_questions = {}

# Функция для очистки текста от HTML-спецсимволов
def format_text(text: str) -> str:
    return html.unescape(text).strip().lower()  # Убираем пробелы и приводим к нижнему регистру

# Функция для получения вопросов из API
def get_question():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    response = requests.get(url).json()
    question_data = response['results'][0]
    
    question = html.unescape(question_data['question'])
    correct_answer = format_text(question_data['correct_answer'])
    incorrect_answers = [format_text(ans) for ans in question_data['incorrect_answers']]
    
    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)
    
    return {
        "question": question,
        "correct_answer": correct_answer,
        "all_answers": all_answers
    }

async def update_stats(user_id: int, is_correct: bool):
    user_id = int(user_id)  # Приводим к int для надежности

    async with aiosqlite.connect("quiz_bot.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

        async with db.execute("SELECT total_questions, correct_answers FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()

        if user:
            await db.execute("UPDATE users SET total_questions = total_questions + 1 WHERE user_id = ?", (user_id,))
            if is_correct:
                await db.execute("UPDATE users SET correct_answers = correct_answers + 1 WHERE user_id = ?", (user_id,))
        else:
            await db.execute("INSERT INTO users (user_id, total_questions, correct_answers) VALUES (?, 1, ?)", (user_id, int(is_correct)))

        await db.commit()


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я викторина-бот. Напиши /quiz, чтобы начать и /stats, чтобы посмотреть свою статистику.")

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    user_id = int(message.from_user.id)

    async with aiosqlite.connect("quiz_bot.db") as db:
        async with db.execute("SELECT total_questions, correct_answers FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()

    print(f"DEBUG: user_id={user_id}, user_data={user}")  # Вывод в консоль

    if user:
        total, correct = user
        await message.answer(f"📊 Твоя статистика:\nВсего вопросов: {total}\nПравильных ответов: {correct}")
    else:
        await message.answer("Ты еще не отвечал на вопросы. Напиши /quiz, чтобы начать!")


# Обработчик команды /quiz
@dp.message(Command("quiz"))
async def quiz(message: types.Message):
    user_id = message.from_user.id
    question_data = get_question()
    user_questions[user_id] = question_data['correct_answer']
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=answer)] for answer in question_data['all_answers']],  
        resize_keyboard=True
    )
    
    await message.answer(f"🎮 **{question_data['question']}**", parse_mode="Markdown", reply_markup=keyboard)

# Обработчик ответов пользователей
@dp.message()
async def handle_answer(message: types.Message):
    if message.text.startswith("/"):
        return  # Игнорируем команды, чтобы они доходили до других обработчиков

    user_id = message.from_user.id
    user_answer = format_text(message.text).strip().lower()  # Приводим к нижнему регистру

    if user_id in user_questions:
        correct_answer = format_text(user_questions.pop(user_id)).strip().lower()
        is_correct = user_answer == correct_answer

        await update_stats(user_id, is_correct)

        if is_correct:
            await message.answer("✅ Правильно!", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer(f"❌ Неправильно! Правильный ответ: {correct_answer}", reply_markup=types.ReplyKeyboardRemove())

        await message.answer("Напиши /quiz для нового вопроса.")
    else:
        await message.answer("Чтобы начать викторину, напиши /quiz.")






async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())