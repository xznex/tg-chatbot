from settings import TG_TOKEN
import telebot
import mysql.connector
# from telebot import types

bot = telebot.TeleBot(TG_TOKEN)

# keyboard_start = telebot.types.ReplyKeyboardMarkup(True, True)
# keyboard_start.row("/start_chat")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    port="3306",
    database="db_prosto_chatbot",
)

cursor = db.cursor()

# cursor.execute("CREATE DATABASE db_prosto_chatbot")

# cursor.execute("SHOW DATABASES")
#
# for x in cursor:
#     print(x)

# cursor.execute("CREATE TABLE users (nickname VARCHAR(255))")
#
# cursor.execute("SHOW TABLES")
#
# for x in cursor:
#     print(x)
#
# cursor.execute("ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)")

# sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
# val = ("John", "Neverov", 1)
# cursor.execute(sql, val)
#
# db.commit()
#
# print(cursor.rowcount, "запись добавлена")

# sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
# val = [
#   ('Peter', 'Lowstreet 4', 2),
#   ('Amy', 'Apple st 652', 3),
#   ('Hannah', 'Mountain 21', 4),
#   ('Michael', 'Valley 345', 5),
# ]
# cursor.executemany(sql, val)
# db.commit()
# print(cursor.rowcount, "записи было добавлено")

# cursor.execute("ALTER TABLE users ADD COLUMN search INT")

# msql = "INSERT INTO users (nickname, id, user_id, search) VALUES (%s, %s, %s, %s)"
# val = [
#   ('Peter', 2, 222222, 1),
#   ('Amy', 3, 3333333, 1),
#   ('Hannah', 4, 44444, 0),
#   ('Michael', 5, 5555555, 1),
# ]
# cursor.executemany(msql, val)
# db.commit()

user_data = {}


class User:
    def __init__(self, nickname):
        self.nickname = nickname
        # self.search = False

    def get_nickname(self):
        return self.nickname

    def __str__(self):
        return f"nickname - {self.nickname}"


def user_exist(message):
    try:
        sql = "SELECT * FROM users WHERE user_id = %s"
        us_id = (message.from_user.id,)
        cursor.execute(sql, us_id)
        result = cursor.fetchall()

        user_data[message.from_user.id] = User(result[0][0])

        # print(user_data[message.from_user.id])
        # print(result)
        # print(type(result[0][2]), type(us_id[0]))

        if result[0][2] == us_id[0]:
            return True

    except Exception:
        return False


@bot.message_handler(commands=["start_chatting"])
def start_chatting(message):
    user_id = message.chat.id

    bot.send_message(message.chat.id, "Поиск собеседника")

    # пользователю присваивается в search True
    sql = "UPDATE users SET search = %s WHERE user_id = %s"
    val = (True, user_id)
    cursor.execute(sql, val)
    db.commit()  # [('dudddy', 1, 627512965, 1)]

    # пользователь начинает искать у кого еще в search есть True
    sql = "SELECT * FROM users WHERE search = 1"
    cursor.execute(sql)
    result = cursor.fetchall()  # [('dudddy', 1, 627512965, 1), ('Peter', 2, 222222, 1), ('Amy', 3, 3333333, 1)]

    if result[1]:
        partner_id = result[1][2]


@bot.message_handler(commands=["register"])
def register_message_nickname(message):
    if user_exist(message):
        bot.send_message(message.chat.id, "Вы уже имеете никнейм. Если хотите поменять - введите /edit_nickname")
    else:
        msg = bot.send_message(message.chat.id, "Какой никнейм хотите выбрать?")
        bot.register_next_step_handler(msg, process_nickname_step)


@bot.message_handler(commands=["show_nickname"])
def show_nickname(message):
    if user_exist(message):
        user_id = message.from_user.id
        user = user_data[user_id]
        bot.send_message(message.chat.id, f"Никнейм, который увидит ваш собеседник - {user.get_nickname()}")
    else:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрировались')


@bot.message_handler(commands=["edit_nickname"])
def edit_nickname(message):
    if user_exist(message):
        msg = bot.send_message(message.chat.id, "Введите новый никнейм")
        bot.register_next_step_handler(msg, process_edit_nickname_step)
    else:
        bot.send_message(message.chat.id, "Для начало вам нужно зарегистрироваться /register")


def process_edit_nickname_step(message):
    # try:
    user_id = message.from_user.id
    user_data[user_id] = User(message.text)
    nickname = user_data[user_id].get_nickname()

    # print(user_id)
    # print(nickname)
    # print(user_data[user_id].get_nickname())
    # for key, value in user_data.items():
    #     print(key, value)

    sql = "UPDATE users SET nickname = %s WHERE user_id = %s"
    val = (user_data[user_id].get_nickname(), user_id)
    cursor.execute(sql, val)
    db.commit()

    bot.send_message(message.chat.id, f"Ваш новый никнейм - {nickname}")

    # except Exception:
    #     bot.send_message(message.chat.id, 'Ошибка')


# def process_first_name_step(message):
#     try:
#         user_id = message.from_user.id
#         user_data[user_id] = User(message.text)
#           (user.last_name = message.text)
#         msg = bot.send_message(message.chat.id, "Введите фамилию")
#         bot.register_next_step_handler(msg, process_last_name_step)
#     except Exception as e:
#         bot.reply_to(message, 'error #1')


def process_nickname_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)
        user = user_data[user_id]

        sql = "INSERT INTO users (nickname, user_id) VALUES (%s, %s)"
        val = (user.nickname, user_id)
        cursor.execute(sql, val)
        db.commit()

        bot.send_message(message.chat.id, "Вы успешно зарегистрированны")
    # for key, value in user_data.items():
    #     print(key, value)
    except Exception:
        bot.send_message(message.chat.id, 'Ошибка, либо вы уже зарегистрированы')


# @bot.message_handler(commands=["start_chat"])
# def start_chat(message):
#     bot.send_message(message.chat.id, "Поиск собеседника...", reply_markup=False)
# 
#     # сам поиск собеседника
# 
#     bot.send_message(message.chat.id,
#                      "Собеседник найден\n/next - искать нового собеседника\n/stop - закончить диалог \n\n Общайтесь",
#                      reply_markup=False)


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling()
