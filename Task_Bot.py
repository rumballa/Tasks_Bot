from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import asyncio

# Список задач
tasks = []
# Стан задач (True - виконана, False - не виконана)
task_statuses = []
# Час нагадування
task_deadlines = []
# Словник для збереження chat_id
user_chat_ids = {}

# Команда старт
async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_chat_ids[chat_id] = chat_id
    await update.message.reply_text('Привіт! Я бот для управління задачами. При роботі зі мною використовуй команди:\n /add - Команда для додавання задачі\n /list - Список всіх задач\n /remove - Видалити задачу\n /complete - Помітити задачу як виконану')

# Команда для додавання задачі
async def add(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 3:
        await update.message.reply_text('Будь ласка, вкажіть задачу і час нагадування у форматі "ГГГГ-ММ-ДД ЧЧ:ММ".')
        return
    
    task = ' '.join(args[:-2])
    deadline_str = f"{args[-2]} {args[-1]}"
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
        tasks.append(task)
        task_statuses.append(False)  # Від самого початку задача не виконана
        task_deadlines.append(deadline)
        await update.message.reply_text(f'Задача "{task}" додана з нагадуванням на {deadline_str}.')

        # Додаємо задачу нагадування в job_queue
        delay = (deadline - datetime.now()).total_seconds()
        context.job_queue.run_once(send_reminder, delay, chat_id=update.message.chat_id, name=task)
    except ValueError:
        await update.message.reply_text('Не правильний формат часу. Будь ласка, використовуйте формат "ГГГГ-ММ-ДД ЧЧ:ММ".')

# Функція для отправки нагадування
async def send_reminder(context: CallbackContext) -> None:
    job = context.job
    chat_id = job.chat_id
    task = job.name
    await context.bot.send_message(chat_id=chat_id, text=f'Нагадування про задачу: {task}')

# Команда для перегляду списка задач
async def list_tasks(update: Update, context: CallbackContext) -> None:
    if tasks:
        message = 'Список задач:\n' + '\n'.join(
            f'{i + 1}. {"✅" if status else "❌"} {task} (Нагадування: {deadline.strftime("%Y-%m-%d %H:%M")})'
            for i, (task, status, deadline) in enumerate(zip(tasks, task_statuses, task_deadlines))
        )
    else:
        message = 'Список задач пустий.'
    await update.message.reply_text(message)

# Команда для видалення задачі за номером
async def remove(update: Update, context: CallbackContext) -> None:
    if context.args and context.args[0].isdigit():
        task_index = int(context.args[0]) - 1
        if 0 <= task_index < len(tasks):
            removed_task = tasks.pop(task_index)
            task_statuses.pop(task_index)
            task_deadlines.pop(task_index)
            await update.message.reply_text(f'Задача "{removed_task}" видалена.')
        else:
            await update.message.reply_text('Некорректний номер задачі.')
    else:
        await update.message.reply_text('Будь ласка, вкажіть номер задачі після команди /remove.')

# Команда для відмічання задачі як виконаної
async def complete(update: Update, context: CallbackContext) -> None:
    if context.args and context.args[0].isdigit():
        task_index = int(context.args[0]) - 1
        if 0 <= task_index < len(tasks):
            task_statuses[task_index] = True
            await update.message.reply_text(f'Задача "{tasks[task_index]}" відмічена як виконана.')
        else:
            await update.message.reply_text('Некорректний номер задачі.')
    else:
        await update.message.reply_text('Будь ласка, вкажіть номер задачі після команди /complete.')

def main() -> None:
    # Токен бота
    token = '7393620404:AAFkVpmcVd4A9s9EDRJLZ5v7HmU9f9pInEA'
    application = Application.builder().token(token).build()

    # Додаємо обробник команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("complete", complete))

    application.run_polling()

if __name__ == '__main__':
    main()
