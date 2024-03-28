import telebot
import requests
import json
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("TOKEN")
api = "API"

# Створив словник для відстеження стану користувачів
user_state = {}


@bot.message_handler(commands=["start", "main"])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_weather = types.KeyboardButton("☀️Прогноз погоди")
    btn_actions = types.KeyboardButton("💰Акції")
    btn_support = types.KeyboardButton("🎖️Підтримати проєкт")
    btn_home = types.KeyboardButton("🏠На головну")
    markup.add(btn_weather, btn_actions, btn_support, btn_home)
    bot.send_message(
        message.chat.id,
        f"Вітаю, Ви в головному меню, оберіть дію⬇️",
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == "🎖️Підтримати проєкт")
def support_project(message):
    text = "Якщо Ви хочете допомогти цьому проєкту, можете зробити внесок у перемогу України над окупантом, натиснувши на цю кнопку⬇️"
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(
        text="💳Зробити внесок", url="https://u24.gov.ua/uk"
    )
    keyboard.add(url_button)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "💰Акції")
def show_promotions(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_velmart = types.KeyboardButton("🏪Акції Велмарт")
    btn_steam = types.KeyboardButton("🎮Акції Steam")
    btn_back = types.KeyboardButton("🔙Назад")
    markup.add(btn_velmart, btn_steam, btn_back)
    bot.send_message(message.chat.id, "Оберіть потрібний розділ:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🏪Акції Велмарт")
def handle_velmart_promotions(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🗓️Товар тижня", "🔥Краща ціна")
    markup.row("🏠На головну")
    bot.send_message(message.chat.id, "Оберіть тип акцій:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🏠На головну")
def go_home(message):
    main(message)


# Фото для товарів тижня
weekly_products_data = [
    {"photo": "tovar1.png", "next_button": "Далі"},
    {"photo": "tovar2.png", "next_button": "Далі"},
    {"photo": "tovar3.png", "next_button": "Далі"},
    {"photo": "tovar4.png", "next_button": "🔙Назад"},
]


@bot.message_handler(func=lambda message: message.text == "🗓️Товар тижня")
def handle_weekly_product(message):
    # Виклик функції для відображення першого товару тижня
    send_weekly_product(message, 0)


def send_weekly_product(message, index):
    product = weekly_products_data[index]
    photo = open(product["photo"], "rb")
    next_button_text = product["next_button"]

    markup = InlineKeyboardMarkup()
    if next_button_text == "🔙Назад":
        markup.add(
            InlineKeyboardButton(text=next_button_text, callback_data="main_menu")
        )
    else:
        markup.add(
            InlineKeyboardButton(
                text=next_button_text, callback_data="next_weekly_product"
            )
        )

    bot.send_photo(message.chat.id, photo, reply_markup=markup)

    # Збереження індексу фотографії в стані користувача
    user_state[message.chat.id] = {"product_index": index}


def get_current_weekly_product_index(message):
    for index, data in enumerate(weekly_products_data):
        if data["photo"] in message.photo:
            return index
    return 0


@bot.callback_query_handler(func=lambda call: call.data == "next_weekly_product")
def next_weekly_product_callback(call):
    chat_id = call.message.chat.id
    current_index = user_state.get(chat_id, {}).get("product_index", 0)
    if current_index < len(weekly_products_data) - 1:
        next_index = current_index + 1
        send_weekly_product(call.message, next_index)
    else:
        main(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu_callback(call):
    main(call.message)


best_price_products_data = [
    {"photo": "product1.png", "next_button": "Далі"},
    {"photo": "product2.png", "next_button": "Далі"},
    {"photo": "product3.png", "next_button": "Далі"},
    {"photo": "product4.png", "next_button": "Далі"},
    {"photo": "product5.png", "next_button": "Далі"},
    {"photo": "product6.png", "next_button": "Далі"},
    {"photo": "product7.png", "next_button": "Далі"},
    {"photo": "product8.png", "next_button": "Далі"},
    {"photo": "product9.png", "next_button": "Далі"},
    {"photo": "product10.png", "next_button": "Далі"},
    {"photo": "product11.png", "next_button": "🔙Назад"},
]


@bot.message_handler(func=lambda message: message.text == "🔥Краща ціна")
def handle_best_price_product(message):
    send_product(message, best_price_products_data)


def send_product(message, product_data):
    index = 0
    send_product_by_index(message, product_data, index)


def send_product_by_index(message, product_data, index):
    product = product_data[index]
    photo = open(product["photo"], "rb")
    next_button_text = product["next_button"]

    markup = InlineKeyboardMarkup()
    if next_button_text == "🔙Назад":
        markup.add(
            InlineKeyboardButton(text=next_button_text, callback_data="main_menu")
        )
    else:
        markup.add(
            InlineKeyboardButton(text=next_button_text, callback_data="next_product")
        )

    bot.send_photo(message.chat.id, photo, reply_markup=markup)

    user_state[message.chat.id] = {"product_index": index, "product_data": product_data}


@bot.callback_query_handler(func=lambda call: call.data == "next_product")
def next_product_callback(call):
    chat_id = call.message.chat.id
    user_data = user_state.get(chat_id, {})
    current_index = user_data.get("product_index", 0)
    product_data = user_data.get("product_data")

    if current_index < len(product_data) - 1:
        next_index = current_index + 1
        send_product_by_index(call.message, product_data, next_index)
    else:
        main(call.message)


# Словник з інформацією про ігри
genre_games = {
    "🎲Глибокий сюжет": [
        {
            "title": "Metro Exodus",
            "link": "https://store.steampowered.com/app/412020/Metro_Exodus/",
        },
        {
            "title": "RESIDENT EVIL 4",
            "link": "https://store.steampowered.com/app/2050650/Resident_Evil_4/",
        },
        {
            "title": "Resident Evil Village",
            "link": "https://store.steampowered.com/app/1196590/Resident_Evil_Village/",
        },
        {
            "title": "RESIDENT EVIL 7 BIOHAZARD",
            "link": "https://store.steampowered.com/app/418370/Resident_Evil_7_Biohazard/",
        },
        {
            "title": "Dying Light",
            "link": "https://store.steampowered.com/app/239140/Dying_Light/",
        },
        {
            "title": "Metro: Last Light Redux",
            "link": "https://store.steampowered.com/app/287390/Metro_Last_Light_Redux/",
        },
        {
            "title": "Mortal Kombat 1",
            "link": "https://store.steampowered.com/app/1971870/Mortal_Kombat_1/",
        },
        {
            "title": "Little Nightmares II",
            "link": "https://store.steampowered.com/app/860510/Little_Nightmares_II/",
        },
        {
            "title": "Dead Space (2008)",
            "link": "https://store.steampowered.com/app/17470/Dead_Space_2008/",
        },
        {
            "title": "ROAD 96 HITCHHIKER BUNDLE",
            "link": "https://store.steampowered.com/bundle/21749/Road_96_Hitchhiker_Bundle/",
        },
        {
            "title": "🕹️Інші ігри жанру",
            "link": "https://store.steampowered.com/search/?tags=1742&category1=998&specials=1&ndl=1",
        },
    ],
    "⚔️Бойовики": [
        {
            "title": "Grand Theft Auto V",
            "link": "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/",
        },
        {
            "title": "STAR WARS™: Battlefront Classic Collection",
            "link": "https://store.steampowered.com/app/2446550/STAR_WARS_Battlefront_Classic_Collection/",
        },
        {
            "title": "Hell Let Loose",
            "link": "https://store.steampowered.com/app/686810/Hell_Let_Loose/",
        },
        {
            "title": "Sniper Elite 5",
            "link": "https://store.steampowered.com/app/1029690/Sniper_Elite_5/",
        },
        {
            "title": "Sniper Elite 4",
            "link": "https://store.steampowered.com/app/312660/Sniper_Elite_4/",
        },
        {
            "title": "ACE COMBAT™ 7: SKIES UNKNOWN",
            "link": "https://store.steampowered.com/app/502500/ACE_COMBAT_7_SKIES_UNKNOWN/",
        },
        {
            "title": "Ghostrunner 2",
            "link": "https://store.steampowered.com/app/2144740/Ghostrunner_2/",
        },
        {
            "title": "Street Fighter V",
            "link": "https://store.steampowered.com/app/310950/Street_Fighter_V/",
        },
        {
            "title": "Insurgency: Sandstorm",
            "link": "https://store.steampowered.com/app/581320/Insurgency_Sandstorm/",
        },
        {
            "title": "Saints Row: The Third",
            "link": "https://store.steampowered.com/app/55230/Saints_Row_The_Third/",
        },
        {
            "title": "🕹️Інші ігри жанру",
            "link": "https://store.steampowered.com/search/?tags=19&category1=998&specials=1&ndl=1",
        },
    ],
    "💻Симулятори": [
        {
            "title": "Forza Horizon 5",
            "link": "https://store.steampowered.com/app/1551360/Forza_Horizon_5/",
        },
        {
            "title": "Forza Horizon 4",
            "link": "https://store.steampowered.com/app/1293830/Forza_Horizon_4/",
        },
        {
            "title": "Dune: Spice Wars",
            "link": "https://store.steampowered.com/app/1605220/Dune_Spice_Wars/",
        },
        {
            "title": "House Flipper 2",
            "link": "https://store.steampowered.com/app/1190970/House_Flipper_2/",
        },
        {
            "title": "Car Mechanic Simulator 2021",
            "link": "https://store.steampowered.com/app/1190000/Car_Mechanic_Simulator_2021/",
        },
        {
            "title": "Kerbal Space Program 2",
            "link": "https://store.steampowered.com/app/954850/Kerbal_Space_Program_2/",
        },
        {
            "title": "Train Sim World® 4",
            "link": "https://store.steampowered.com/app/2362300/Train_Sim_World_4/",
        },
        {
            "title": "Gas Station Simulator",
            "link": "https://store.steampowered.com/app/1149620/Gas_Station_Simulator/",
        },
        {
            "title": "LEGO® Bricktales",
            "link": "https://store.steampowered.com/app/1898290/LEGO_Bricktales/",
        },
        {
            "title": "The Long Dark",
            "link": "https://store.steampowered.com/app/305620/The_Long_Dark/",
        },
        {
            "title": "🕹️Інші ігри жанру",
            "link": "https://store.steampowered.com/search/?tags=599&category1=998&specials=1&ndl=1",
        },
    ],
    "🛫Мандрівні ігри": [
        {
            "title": "Wizard with a Gun",
            "link": "https://store.steampowered.com/app/1150530/Wizard_with_a_Gun/",
        },
        {
            "title": "Othercide",
            "link": "https://store.steampowered.com/app/798490/Othercide/",
        },
        {
            "title": "Curious Expedition 2",
            "link": "https://store.steampowered.com/app/1040230/Curious_Expedition_2/",
        },
        {
            "title": "Iratus: Lord of the Dead",
            "link": "https://store.steampowered.com/app/807120/Iratus_Lord_of_the_Dead/",
        },
        {
            "title": "Gods Will Fall",
            "link": "https://store.steampowered.com/app/1243690/Gods_Will_Fall/",
        },
        {
            "title": "Mage and Monsters",
            "link": "https://store.steampowered.com/app/1950440/Mage_and_Monsters/",
        },
        {
            "title": "Tavern Cards",
            "link": "https://store.steampowered.com/app/1221240/Tavern_Cards/",
        },
        {
            "title": "Swordship",
            "link": "https://store.steampowered.com/app/1804270/Swordship/",
        },
        {
            "title": "The Last City",
            "link": "https://store.steampowered.com/app/2001280/The_Last_City/",
        },
        {
            "title": "Infectonator: Survivors",
            "link": "https://store.steampowered.com/app/269310/Infectonator_Survivors/",
        },
        {
            "title": "🕹️Інші ігри жанру",
            "link": "https://store.steampowered.com/search/?tags=1716&category1=998&specials=1&ndl=1",
        },
    ],
    "🗺️Відкритий світ": [
        {
            "title": "Black Desert",
            "link": "https://store.steampowered.com/app/582660/Black_Desert/",
        },
        {
            "title": "Green Hell",
            "link": "https://store.steampowered.com/app/815370/Green_Hell/",
        },
        {
            "title": "The Ascent",
            "link": "https://store.steampowered.com/app/979690/The_Ascent/",
        },
        {
            "title": "The Walking Dead: Saints & Sinners",
            "link": "https://store.steampowered.com/app/1947500/The_Walking_Dead_Saints__Sinners__Chapter_2_Retribution/",
        },
        {
            "title": "Medal of Honor™: Above and Beyond",
            "link": "https://store.steampowered.com/app/1402320/Medal_of_Honor_Above_and_Beyond/",
        },
        {
            "title": "DESOLATE",
            "link": "https://store.steampowered.com/app/671510/DESOLATE/",
        },
        {
            "title": "House Builder",
            "link": "https://store.steampowered.com/app/1244630/House_Builder/",
        },
        {
            "title": "112 Operator",
            "link": "https://store.steampowered.com/app/793460/112_Operator/",
        },
        {
            "title": "Far Lands",
            "link": "https://store.steampowered.com/app/1500940/Far_Lands/",
        },
        {
            "title": "King of Seas",
            "link": "https://store.steampowered.com/app/1209410/King_of_Seas/",
        },
        {
            "title": "🕹️Інші ігри жанру",
            "link": "https://store.steampowered.com/search/?tags=1695&category1=998&specials=1&ndl=1",
        },
    ],
    "💊Виживання": [
        {
            "title": "Frostpunk",
            "link": "https://store.steampowered.com/app/323190/Frostpunk/",
        },
        {
            "title": "Medieval Dynasty",
            "link": "https://store.steampowered.com/app/1129580/Medieval_Dynasty/",
        },
        {
            "title": "DRAGON BALL: THE BREAKERS",
            "link": "https://store.steampowered.com/app/1276760/DRAGON_BALL_THE_BREAKERS/",
        },
        {
            "title": "Unrailed!",
            "link": "https://store.steampowered.com/app/1016920/Unrailed/",
        },
        {
            "title": "RESIDENT EVIL 2 / BIOHAZARD RE:2 DELUXE EDITION",
            "link": "https://store.steampowered.com/sub/281610/",
        },
        {
            "title": "CryoFall",
            "link": "https://store.steampowered.com/app/829590/CryoFall/",
        },
        {
            "title": "In Silence",
            "link": "https://store.steampowered.com/app/1361000/In_Silence/",
        },
        {
            "title": "Talk to Strangers",
            "link": "https://store.steampowered.com/app/963280/Talk_to_Strangers/",
        },
        {
            "title": "Among Us",
            "link": "https://store.steampowered.com/app/945360/Among_Us/",
        },
        {
            "title": "Chernobylite Enhanced Edition",
            "link": "https://store.steampowered.com/app/1016800/Chernobylite_Enhanced_Edition/",
        },
        {
            "title": "🕹️Інші ігри жанру",
            "link": "https://store.steampowered.com/search/?tags=1662&category1=998&specials=1&ndl=1",
        },
    ],
}


# Обробник для кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == "🔙Назад")
def back_to_main_menu(message):
    main(message)


@bot.message_handler(func=lambda message: message.text == "🎮Акції Steam")
def show_promotions(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    genre_buttons = [
        types.KeyboardButton("🎲Глибокий сюжет"),
        types.KeyboardButton("⚔️Бойовики"),
        types.KeyboardButton("💻Симулятори"),
        types.KeyboardButton("🛫Мандрівні ігри"),
        types.KeyboardButton("🗺️Відкритий світ"),
        types.KeyboardButton("💊Виживання"),
        types.KeyboardButton("🔙Назад"),
    ]
    markup.add(*genre_buttons)
    bot.send_message(message.chat.id, "Оберіть жанр ігор:", reply_markup=markup)


# Обробник для жанру ігор
@bot.message_handler(func=lambda message: message.text in genre_games.keys())
def show_genre_games(message):
    genre = message.text
    bot.send_message(message.chat.id, f"Вибрано жанр ігор: {genre}")

    # Отримуємо список ігор для обраного жанру
    games_list = genre_games[genre]

    # Вибираємо фотографію в залежності від жанру
    if genre == "🎲Глибокий сюжет":
        photo_path = "story_games.jpg"
    elif genre == "⚔️Бойовики":
        photo_path = "action_games.jpg"
    elif genre == "💻Симулятори":
        photo_path = "simulator_games.jpg"
    elif genre == "🛫Мандрівні ігри":
        photo_path = "adventure_games.jpg"
    elif genre == "🗺️Відкритий світ":
        photo_path = "open_world_games.jpg"
    elif genre == "💊Виживання":
        photo_path = "survival_games.jpg"
    else:
        photo_path = "default_image.jpg"

    # Вивід фото жанру
    bot.send_photo(
        message.chat.id,
        photo=open(photo_path, "rb"),
    )

    # Створення інлайн клавіатури з іграми даного жанру
    markup = types.InlineKeyboardMarkup(row_width=2)
    games_buttons = [
        types.InlineKeyboardButton(text=game["title"], url=game["link"])
        for game in games_list
    ]
    markup.add(*games_buttons)
    bot.send_message(
        message.chat.id, "Акційні ігри в цьому жанрі:", reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "☀️Прогноз погоди")
def request_city(message):
    user_state[message.chat.id] = "weather"
    bot.send_message(message.chat.id, "Напишіть назву міста:")


@bot.message_handler(func=lambda message: message.text == "🏠На головну")
def go_home(message):
    # Скидання стану користувача, якщо він переходить на головну сторінку
    user_state[message.chat.id] = None
    main(message)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Перевірка, чи користувач виконує запит на прогноз погоди
    if user_state.get(message.chat.id) == "weather":
        city = message.text.strip().lower()
        res = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric&lang=ua"
        )
        if res.status_code == 200:
            balbes = json.loads(res.text)
            description = balbes["weather"][0]["description"]
            words = description.split(maxsplit=1)
            temp = balbes["main"]["temp"]
            with open("./weatherfor.png", "rb") as photo_file:
                if len(words) > 1:
                    capitalized_first_word = words[0].capitalize()
                    bot.send_photo(
                        message.chat.id,
                        photo_file,
                        caption=f"<b>☀️Погода зараз:</b> {capitalized_first_word} {words[1]} \n<b>🌡️Температура</b>: {temp}°C \n<b>❄️Відчувається як</b>: {balbes['main']['feels_like']}°C \n<b>💧Вологість:</b> {balbes['main']['humidity']}% \n<b>🌫️Видимість:</b> {balbes['visibility']}м \n<b>🌪️Швидкість вітру:</b> {balbes['wind']['speed']}м/с \n<b>🧭Напрямок вітру:</b> {balbes['wind']['deg']}°",
                        parse_mode="html",
                    )
                else:
                    capitalized_first_word = description.capitalize()
                    bot.send_photo(
                        message.chat.id,
                        photo_file,
                        caption=f"<b>☀️Погода зараз:</b> {capitalized_first_word} \n<b>🌡️Температура</b>: {temp}°C \n<b>❄️Відчувається як</b>: {balbes['main']['feels_like']}°C \n<b>💧Вологість:</b> {balbes['main']['humidity']}% \n<b>🌫️Видимість:</b> {balbes['visibility']}м \n<b>🌪️Швидкість вітру:</b> {balbes['wind']['speed']}м/с \n<b>🧭Напрямок вітру:</b> {balbes['wind']['deg']}°",
                        parse_mode="html",
                    )
            # Збереження стану користувача для повторного введення міста
            user_state[message.chat.id] = "weather"
        else:
            bot.reply_to(
                message,
                "<b>⚠️Некоректне введення.</b> \nЩоб отримати прогноз погоди, натисніть кнопку '<u>Прогноз погоди</u>'.",
                parse_mode="html",
            )
            # Видалення стану користувача після невдалого пошуку
            del user_state[message.chat.id]
    else:
        bot.reply_to(
            message,
            "⚠️Не розумію вашого повідомлення. \nВиберіть необхідний пункт меню.⬇️",
            parse_mode="html",
        )


bot.polling(none_stop=True)
