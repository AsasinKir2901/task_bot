
from telebot import TeleBot
import telebot

from logic import TaskManager
from config import TOKEN, DATABASE


bot = TeleBot(TOKEN)

task_manager = TaskManager(DATABASE)
task_manager.create_table()


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(
        message.chat.id,
        """Привет! Я бот-менеджер задач.
Помогу тебе сохранить свои задачи!

/add_task — добавить задачу
/delete_task — удалить задачу
/show — показать все задачи
/show 5 — показать первые 5 задач"""
    )


@bot.message_handler(commands=["add_task"])
def addtask_command(message):
    msg = bot.send_message(
        message.chat.id,
        "Введите название задачи:"
    )
    bot.register_next_step_handler(msg, save_task)


def save_task(message):
    if not message.text or message.text.startswith("/"):
        bot.send_message(
            message.chat.id,
            "Добавление отменено. Используй /add_task снова."
        )
        return

    name = message.text.strip()

    if not name:
        bot.send_message(message.chat.id, "Название не может быть пустым.")
        return

    user_id = message.from_user.id

    task_manager.add_task(user_id, name, "")

    bot.send_message(message.chat.id, "Задача добавлена!")


@bot.message_handler(commands=["delete_task"])
def deletetask_command(message):
    msg = bot.send_message(
        message.chat.id,
        "Введите название задачи, которую хотите удалить:"
    )
    bot.register_next_step_handler(msg, delete_task_by_id)


def delete_task_by_id(message):
    if not message.text or message.text.startswith("/"):
        bot.send_message(message.chat.id, "Удаление отменено.")
        return

    user_id = message.from_user.id
    task_name = message.text.strip()

    deleted = task_manager.delete_task(task_name, user_id)

    if deleted:
        bot.send_message(message.chat.id, "Задача удалена.")
    else:
        bot.send_message(message.chat.id, "Задача не найдена.")


@bot.message_handler(commands=["show"])
def show(message):
    user_id = message.from_user.id
    arg = telebot.util.extract_arguments(message.text).strip()

    if arg:
        try:
            num = int(arg)

            if num <= 0:
                raise ValueError

            tasks = task_manager.show_task_many(user_id, num)

        except ValueError:
            bot.send_message(
                message.chat.id,
                "Укажи положительное число. Например: /show 5"
            )
            return
    else:
        tasks = task_manager.show_task_all(user_id)

    if tasks:
        text = "\n".join(x[0] for x in tasks)
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Задач нет.")


if __name__ == "__main__":
    bot.infinity_polling()
