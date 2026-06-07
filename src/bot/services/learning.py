from dataclasses import dataclass
from datetime import datetime
import random

from sqlalchemy import Select, delete, func, select
from sqlalchemy.orm import Session, joinedload

from src.bot.database.models import (
    QuizAttempt,
    User,
    UserWord,
    UserWordProgress,
    WordCard,
    WordSet,
)


CUSTOM_WORD_SET_CODE = "custom_user_words"
SPECIAL_SET_CODES = {"dictionary", "weak", "survival"}
SPECIAL_WORD_SETS = [
    ("dictionary", "Тест по словарю"),
    ("weak", "Повторение ошибок"),
    ("survival", "До первой ошибки"),
]
DAILY_GOAL_TESTS = 1
SUPPORTED_LANGUAGES = {
    "English": "Английский",
    "Spanish": "Испанский",
    "Italian": "Итальянский",
}
LANGUAGE_CODE_PREFIX = {
    "English": "en",
    "Spanish": "es",
    "Italian": "it",
}
LANGUAGE_EXAMPLE_TEMPLATES = {
    "Spanish": "Uso «{word}» en una conversación real.",
    "Italian": "Uso «{word}» in una conversazione reale.",
}

DEFAULT_WORD_SETS = [
    {
        "code": "travel_a1",
        "title": "Путешествия: базовый набор",
        "level": "A1",
        "description": "Простые слова для дороги, транспорта и отеля.",
        "cards": [
            ("ticket", "билет", "I need to buy a train ticket."),
            ("airport", "аэропорт", "The airport is 20 minutes from the city center."),
            ("hotel", "отель", "Our hotel is near the museum."),
            ("map", "карта", "Can you show me the city map?"),
            ("passport", "паспорт", "Please show your passport at check-in."),
            ("station", "станция", "The station is across the street."),
            ("luggage", "багаж", "My luggage is too heavy."),
            ("guide", "гид", "The guide told us about the old castle."),
            ("bus", "автобус", "The bus stops near the hotel."),
            ("taxi", "такси", "We took a taxi to the airport."),
            ("room", "комната", "Our room is on the third floor."),
            ("trip", "поездка", "The trip was very comfortable."),
        ],
    },
    {
        "code": "daily_a1",
        "title": "Повседневное общение",
        "level": "A1",
        "description": "Часто используемая лексика для ежедневных диалогов.",
        "cards": [
            ("friend", "друг", "My friend lives in London."),
            ("work", "работа", "She goes to work by bus."),
            ("family", "семья", "My family likes to travel together."),
            ("evening", "вечер", "We usually walk in the evening."),
            ("morning", "утро", "I read the news in the morning."),
            ("street", "улица", "Their house is on a quiet street."),
            ("window", "окно", "Please open the window."),
            ("phone", "телефон", "My phone is in my backpack."),
            ("chair", "стул", "There is a chair near the table."),
            ("door", "дверь", "Close the door, please."),
            ("kitchen", "кухня", "The kitchen is very small."),
            ("music", "музыка", "I listen to music every day."),
        ],
    },
    {
        "code": "food_a1",
        "title": "Еда и кафе",
        "level": "A1",
        "description": "Базовые слова для заказа еды и общения в ресторане.",
        "cards": [
            ("menu", "меню", "Could I see the menu, please?"),
            ("breakfast", "завтрак", "Breakfast starts at 8 a.m."),
            ("water", "вода", "I would like a glass of water."),
            ("bill", "счет", "Could you bring the bill, please?"),
            ("dessert", "десерт", "We ordered dessert after dinner."),
            ("soup", "суп", "Today's soup is tomato soup."),
            ("coffee", "кофе", "He drinks coffee every morning."),
            ("plate", "тарелка", "There is a clean plate on the table."),
            ("bread", "хлеб", "This bread is very fresh."),
            ("tea", "чай", "Would you like some tea?"),
            ("salad", "салат", "She ordered a green salad."),
            ("apple", "яблоко", "I eat an apple every afternoon."),
        ],
    },
    {
        "code": "study_a2",
        "title": "Учеба и университет",
        "level": "A2",
        "description": "Лексика для занятий, расписания и учебных задач.",
        "cards": [
            ("lesson", "урок", "Our lesson starts at ten."),
            ("teacher", "учитель", "The teacher explained the grammar rule."),
            ("student", "студент", "Every student got a task."),
            ("homework", "домашнее задание", "I finished my homework in the evening."),
            ("notebook", "тетрадь", "Write the answer in your notebook."),
            ("library", "библиотека", "She studies in the library every Friday."),
            ("exam", "экзамен", "The exam will be next week."),
            ("question", "вопрос", "I asked the teacher a question."),
            ("answer", "ответ", "Her answer was correct."),
            ("schedule", "расписание", "Check the schedule before class."),
            ("subject", "предмет", "Math is my favorite subject."),
            ("project", "проект", "We are working on a group project."),
        ],
    },
    {
        "code": "city_a2",
        "title": "Город и ориентирование",
        "level": "A2",
        "description": "Слова для прогулок по городу и поиска нужных мест.",
        "cards": [
            ("bridge", "мост", "The bridge connects the two parts of the city."),
            ("square", "площадь", "Let's meet in the main square."),
            ("museum", "музей", "This museum is famous for modern art."),
            ("park", "парк", "We had lunch in the park."),
            ("corner", "угол", "Turn left at the next corner."),
            ("traffic", "движение", "There is a lot of traffic today."),
            ("avenue", "проспект", "Their office is on the central avenue."),
            ("building", "здание", "That building is more than 100 years old."),
            ("crosswalk", "пешеходный переход", "Use the crosswalk near the school."),
            ("fountain", "фонтан", "Children are playing near the fountain."),
            ("subway", "метро", "The subway station is under the mall."),
            ("district", "район", "This district is very quiet."),
        ],
    },
    {
        "code": "shopping_a2",
        "title": "Покупки",
        "level": "A2",
        "description": "Слова для магазинов, оплаты и выбора товаров.",
        "cards": [
            ("price", "цена", "The price is written on the label."),
            ("cash", "наличные", "Do you pay in cash or by card?"),
            ("receipt", "чек", "Please keep your receipt."),
            ("size", "размер", "This shirt is the wrong size."),
            ("store", "магазин", "The store closes at nine."),
            ("discount", "скидка", "There is a discount on these shoes."),
            ("bag", "пакет", "Would you like a bag?"),
            ("card", "карта", "I paid by card at the supermarket."),
            ("customer", "покупатель", "The customer asked for help."),
            ("shelf", "полка", "The milk is on the top shelf."),
            ("market", "рынок", "We bought fruit at the market."),
            ("jacket", "куртка", "This jacket is too expensive."),
        ],
    },
    {
        "code": "work_b1",
        "title": "Работа и карьера",
        "level": "B1",
        "description": "Более содержательная лексика для офиса и рабочих задач.",
        "cards": [
            ("meeting", "встреча", "We have a meeting after lunch."),
            ("deadline", "срок", "The deadline is next Monday."),
            ("manager", "менеджер", "The manager approved the report."),
            ("salary", "зарплата", "Her salary increased this year."),
            ("interview", "собеседование", "He prepared for the interview carefully."),
            ("colleague", "коллега", "My colleague helped me with the task."),
            ("report", "отчет", "Please send the report by email."),
            ("career", "карьера", "She wants to build an international career."),
            ("vacancy", "вакансия", "They posted a new vacancy online."),
            ("promotion", "повышение", "He got a promotion last month."),
            ("department", "отдел", "Our department moved to a new office."),
            ("agreement", "соглашение", "Both sides signed the agreement."),
        ],
    },
    {
        "code": "health_b1",
        "title": "Здоровье и самочувствие",
        "level": "B1",
        "description": "Лексика для описания самочувствия и обращения к врачу.",
        "cards": [
            ("headache", "головная боль", "I stayed home because of a headache."),
            ("medicine", "лекарство", "Take this medicine twice a day."),
            ("appointment", "прием", "I made a doctor's appointment for Friday."),
            ("treatment", "лечение", "The treatment lasted two weeks."),
            ("exercise", "упражнение", "Exercise is important for your health."),
            ("fever", "температура", "The child has a high fever."),
            ("symptom", "симптом", "Cough is a common symptom."),
            ("injury", "травма", "He missed the game because of an injury."),
            ("recovery", "восстановление", "Her recovery was quite fast."),
            ("diet", "диета", "The doctor recommended a special diet."),
            ("clinic", "клиника", "The clinic opens at eight."),
            ("pain", "боль", "He felt pain in his shoulder."),
        ],
    },
    {
        "code": "technology_b2",
        "title": "Технологии и интернет",
        "level": "B2",
        "description": "Лексика для общения о цифровой среде и инструментах.",
        "cards": [
            ("device", "устройство", "This device is connected to the network."),
            ("security", "безопасность", "Online security is very important."),
            ("software", "программное обеспечение", "We need to update the software."),
            ("database", "база данных", "The database stores user information."),
            ("feature", "функция", "The new feature is easy to use."),
            ("account", "аккаунт", "Please verify your account."),
            ("network", "сеть", "The network is unstable today."),
            ("backup", "резервная копия", "Create a backup before the update."),
            ("privacy", "конфиденциальность", "Users care about privacy online."),
            ("access", "доступ", "Only admins have access to this page."),
            ("platform", "платформа", "The platform supports multiple languages."),
            ("upgrade", "обновление", "The upgrade improved performance."),
        ],
    },
]

EXTRA_WORD_SET_BLUEPRINTS = [
    ("home_a1", "Дом и быт", "A1", "Предметы дома и простые бытовые действия.", [("bed", "кровать"), ("lamp", "лампа"), ("floor", "пол"), ("wall", "стена"), ("table", "стол"), ("sofa", "диван"), ("bathroom", "ванная"), ("mirror", "зеркало")]),
    ("clothes_a1", "Одежда", "A1", "Базовая лексика для описания одежды.", [("shirt", "рубашка"), ("dress", "платье"), ("shoes", "обувь"), ("hat", "шляпа"), ("coat", "пальто"), ("pants", "брюки"), ("skirt", "юбка"), ("sweater", "свитер")]),
    ("numbers_time_a1", "Числа и время", "A1", "Слова для времени, дат и простых чисел.", [("minute", "минута"), ("hour", "час"), ("day", "день"), ("week", "неделя"), ("month", "месяц"), ("year", "год"), ("today", "сегодня"), ("tomorrow", "завтра")]),
    ("people_a1", "Люди и внешность", "A1", "Простые слова для описания людей.", [("man", "мужчина"), ("woman", "женщина"), ("child", "ребенок"), ("boy", "мальчик"), ("girl", "девочка"), ("hair", "волосы"), ("eyes", "глаза"), ("smile", "улыбка")]),
    ("weather_a1", "Погода", "A1", "Базовые слова о погоде.", [("sun", "солнце"), ("rain", "дождь"), ("snow", "снег"), ("wind", "ветер"), ("cloud", "облако"), ("cold", "холодно"), ("hot", "жарко"), ("warm", "тепло")]),
    ("animals_a1", "Животные", "A1", "Популярные названия животных.", [("dog", "собака"), ("cat", "кошка"), ("bird", "птица"), ("fish", "рыба"), ("horse", "лошадь"), ("cow", "корова"), ("mouse", "мышь"), ("rabbit", "кролик")]),
    ("school_a1", "Школа", "A1", "Слова для учебных предметов и класса.", [("book", "книга"), ("pen", "ручка"), ("pencil", "карандаш"), ("desk", "парта"), ("board", "доска"), ("class", "класс"), ("bag", "сумка"), ("page", "страница")]),
    ("family_a1", "Семья", "A1", "Базовые слова о семье.", [("mother", "мама"), ("father", "папа"), ("sister", "сестра"), ("brother", "брат"), ("grandmother", "бабушка"), ("grandfather", "дедушка"), ("parents", "родители"), ("baby", "младенец")]),
    ("hobbies_a1", "Хобби", "A1", "Простые слова для свободного времени.", [("game", "игра"), ("movie", "фильм"), ("sport", "спорт"), ("dance", "танец"), ("photo", "фото"), ("song", "песня"), ("walk", "прогулка"), ("reading", "чтение")]),
    ("directions_a2", "Маршрут и направления", "A2", "Как объяснить дорогу и понять маршрут.", [("left", "налево"), ("right", "направо"), ("straight", "прямо"), ("near", "рядом"), ("far", "далеко"), ("behind", "позади"), ("between", "между"), ("opposite", "напротив")]),
    ("transport_a2", "Транспорт", "A2", "Городской транспорт и поездки.", [("tram", "трамвай"), ("train", "поезд"), ("flight", "рейс"), ("platform", "платформа"), ("driver", "водитель"), ("route", "маршрут"), ("delay", "задержка"), ("transfer", "пересадка")]),
    ("hotel_a2", "Отель", "A2", "Заселение, номер и сервис.", [("reception", "ресепшен"), ("reservation", "бронь"), ("key", "ключ"), ("elevator", "лифт"), ("guest", "гость"), ("towel", "полотенце"), ("check-in", "заселение"), ("checkout", "выезд")]),
    ("restaurant_a2", "Ресторан", "A2", "Фразы и слова для кафе и ресторана.", [("waiter", "официант"), ("order", "заказ"), ("dish", "блюдо"), ("fork", "вилка"), ("knife", "нож"), ("spoon", "ложка"), ("taste", "вкус"), ("spicy", "острый")]),
    ("internet_a2", "Интернет", "A2", "Базовая цифровая лексика.", [("password", "пароль"), ("website", "сайт"), ("message", "сообщение"), ("email", "электронная почта"), ("download", "загрузка"), ("upload", "выгрузка"), ("screen", "экран"), ("link", "ссылка")]),
    ("emotions_a2", "Эмоции", "A2", "Как описать состояние и настроение.", [("happy", "счастливый"), ("sad", "грустный"), ("angry", "злой"), ("tired", "уставший"), ("worried", "обеспокоенный"), ("calm", "спокойный"), ("excited", "взволнованный"), ("bored", "скучающий")]),
    ("sports_a2", "Спорт", "A2", "Тренировки, игры и соревнования.", [("team", "команда"), ("player", "игрок"), ("match", "матч"), ("score", "счет"), ("goal", "гол"), ("coach", "тренер"), ("training", "тренировка"), ("winner", "победитель")]),
    ("nature_a2", "Природа", "A2", "Пейзажи и природные объекты.", [("forest", "лес"), ("river", "река"), ("mountain", "гора"), ("lake", "озеро"), ("island", "остров"), ("field", "поле"), ("flower", "цветок"), ("tree", "дерево")]),
    ("chores_a2", "Домашние дела", "A2", "Повседневные обязанности по дому.", [("clean", "убирать"), ("wash", "мыть"), ("cook", "готовить"), ("repair", "чинить"), ("dust", "пыль"), ("laundry", "стирка"), ("trash", "мусор"), ("vacuum", "пылесосить")]),
    ("office_b1", "Офисная коммуникация", "B1", "Рабочие переписки, встречи и задачи.", [("agenda", "повестка"), ("feedback", "обратная связь"), ("proposal", "предложение"), ("task", "задача"), ("update", "обновление"), ("priority", "приоритет"), ("request", "запрос"), ("summary", "резюме")]),
    ("business_b1", "Бизнес", "B1", "Лексика для компаний и процессов.", [("market", "рынок"), ("client", "клиент"), ("budget", "бюджет"), ("profit", "прибыль"), ("contract", "договор"), ("brand", "бренд"), ("growth", "рост"), ("strategy", "стратегия")]),
    ("travel_b1", "Путешествия B1", "B1", "Более сложные ситуации в поездках.", [("customs", "таможня"), ("insurance", "страховка"), ("itinerary", "маршрут"), ("destination", "пункт назначения"), ("accommodation", "жилье"), ("cancellation", "отмена"), ("boarding", "посадка"), ("departure", "отправление")]),
    ("culture_b1", "Культура", "B1", "Искусство, события и впечатления.", [("exhibition", "выставка"), ("performance", "выступление"), ("audience", "аудитория"), ("tradition", "традиция"), ("heritage", "наследие"), ("festival", "фестиваль"), ("sculpture", "скульптура"), ("painting", "картина")]),
    ("education_b1", "Образование B1", "B1", "Учебные процессы и академическая жизнь.", [("assignment", "задание"), ("lecture", "лекция"), ("research", "исследование"), ("degree", "степень"), ("campus", "кампус"), ("deadline", "дедлайн"), ("grade", "оценка"), ("essay", "эссе")]),
    ("relationships_b1", "Отношения", "B1", "Общение, дружба и социальные ситуации.", [("trust", "доверие"), ("support", "поддержка"), ("argument", "спор"), ("advice", "совет"), ("neighbor", "сосед"), ("community", "сообщество"), ("respect", "уважение"), ("promise", "обещание")]),
    ("media_b1", "Медиа", "B1", "Новости, контент и коммуникации.", [("headline", "заголовок"), ("article", "статья"), ("source", "источник"), ("broadcast", "трансляция"), ("interview", "интервью"), ("editor", "редактор"), ("channel", "канал"), ("review", "обзор")]),
    ("finance_b1", "Финансы", "B1", "Деньги, счета и планирование.", [("income", "доход"), ("expense", "расход"), ("loan", "кредит"), ("account", "счет"), ("savings", "сбережения"), ("payment", "платеж"), ("currency", "валюта"), ("interest", "процент")]),
    ("environment_b1", "Экология", "B1", "Окружающая среда и устойчивость.", [("pollution", "загрязнение"), ("recycling", "переработка"), ("waste", "отходы"), ("climate", "климат"), ("energy", "энергия"), ("resource", "ресурс"), ("emission", "выброс"), ("wildlife", "дикая природа")]),
    ("leisure_b1", "Досуг и впечатления", "B1", "Лексика для описания свободного времени и личного опыта.", [("experience", "опыт"), ("impression", "впечатление"), ("activity", "занятие"), ("event", "событие"), ("recommendation", "рекомендация"), ("atmosphere", "атмосфера"), ("memory", "воспоминание"), ("entertainment", "развлечение")]),
    ("career_b2", "Карьера B2", "B2", "Профессиональный рост и управление.", [("leadership", "лидерство"), ("negotiation", "переговоры"), ("expertise", "экспертиза"), ("responsibility", "ответственность"), ("achievement", "достижение"), ("evaluation", "оценка"), ("initiative", "инициатива"), ("competence", "компетенция")]),
    ("science_b2", "Наука", "B2", "Исследования, гипотезы и открытия.", [("evidence", "доказательство"), ("experiment", "эксперимент"), ("hypothesis", "гипотеза"), ("discovery", "открытие"), ("analysis", "анализ"), ("method", "метод"), ("sample", "образец"), ("theory", "теория")]),
    ("law_b2", "Право и правила", "B2", "Юридическая и официальная лексика.", [("regulation", "регулирование"), ("agreement", "соглашение"), ("requirement", "требование"), ("violation", "нарушение"), ("permission", "разрешение"), ("liability", "ответственность"), ("claim", "претензия"), ("procedure", "процедура")]),
    ("politics_b2", "Общество и политика", "B2", "Общественные процессы и решения.", [("policy", "политика"), ("election", "выборы"), ("citizen", "гражданин"), ("debate", "дебаты"), ("reform", "реформа"), ("campaign", "кампания"), ("authority", "власть"), ("rights", "права")]),
    ("psychology_b2", "Психология", "B2", "Мышление, привычки и поведение.", [("behavior", "поведение"), ("memory", "память"), ("attention", "внимание"), ("motivation", "мотивация"), ("habit", "привычка"), ("perception", "восприятие"), ("stress", "стресс"), ("confidence", "уверенность")]),
    ("technology_work_b2", "IT и продукты", "B2", "Разработка, продукты и цифровые команды.", [("interface", "интерфейс"), ("workflow", "рабочий процесс"), ("integration", "интеграция"), ("deployment", "развертывание"), ("performance", "производительность"), ("scalability", "масштабируемость"), ("prototype", "прототип"), ("release", "релиз")]),
    ("academic_b2", "Академический английский", "B2", "Слова для докладов, отчетов и статей.", [("abstract", "аннотация"), ("argument", "аргумент"), ("citation", "цитирование"), ("conclusion", "вывод"), ("framework", "структура"), ("relevance", "актуальность"), ("limitation", "ограничение"), ("source", "источник")]),
    ("advanced_travel_b2", "Международная среда", "B2", "Лексика для общения за границей и работы в международной команде.", [("relocation", "переезд"), ("adaptation", "адаптация"), ("diversity", "разнообразие"), ("background", "происхождение"), ("fluency", "беглость"), ("expectation", "ожидание"), ("boundary", "граница"), ("opportunity", "возможность")]),
]


EXTRA_WORD_EXAMPLES = {
    "bed": "I make my bed every morning.",
    "lamp": "The lamp on my desk is very bright.",
    "floor": "The floor in the kitchen is clean.",
    "wall": "There is a small picture on the wall.",
    "table": "We have dinner at the table.",
    "sofa": "I like reading on the sofa.",
    "bathroom": "The bathroom is next to the bedroom.",
    "mirror": "She looked in the mirror before leaving.",
    "shirt": "He wore a white shirt to the meeting.",
    "dress": "She bought a new dress for the party.",
    "shoes": "My shoes are wet after the rain.",
    "hat": "He put on a hat because it was sunny.",
    "coat": "Take your coat, it is cold outside.",
    "pants": "These pants are too long for me.",
    "skirt": "She chose a blue skirt for work.",
    "sweater": "This sweater is warm and comfortable.",
    "minute": "The bus will arrive in one minute.",
    "hour": "The lesson lasts one hour.",
    "day": "It was a busy day at school.",
    "week": "We have a test next week.",
    "month": "I started learning English last month.",
    "year": "This year I want to travel more.",
    "today": "Today I will repeat ten new words.",
    "tomorrow": "Tomorrow we are going to the museum.",
    "man": "The man asked for directions.",
    "woman": "The woman smiled and said hello.",
    "child": "The child played in the park.",
    "boy": "The boy is reading a comic book.",
    "girl": "The girl is drawing a picture.",
    "hair": "Her hair is short and dark.",
    "eyes": "His eyes are green.",
    "smile": "A friendly smile can start a conversation.",
    "sun": "The sun is shining today.",
    "rain": "The rain started in the evening.",
    "snow": "The snow covered the streets.",
    "wind": "The wind was strong near the river.",
    "cloud": "A dark cloud appeared in the sky.",
    "cold": "It is cold in the morning.",
    "hot": "It is too hot to run outside.",
    "warm": "The room is warm and quiet.",
    "dog": "The dog waited near the door.",
    "cat": "The cat slept on the sofa.",
    "bird": "A bird flew over the garden.",
    "fish": "We saw a fish in the clear water.",
    "horse": "The horse ran across the field.",
    "cow": "The cow stood near the farm gate.",
    "mouse": "A mouse ran under the table.",
    "rabbit": "The rabbit jumped into the grass.",
    "book": "I borrowed a book from the library.",
    "pen": "Can I borrow your pen?",
    "pencil": "The pencil is in my bag.",
    "desk": "Her desk is near the window.",
    "board": "The teacher wrote the rule on the board.",
    "class": "Our class starts at nine.",
    "bag": "I put my notebook in the bag.",
    "page": "Open your book on page ten.",
    "mother": "My mother cooks breakfast every morning.",
    "father": "His father works in a bank.",
    "sister": "My sister studies at university.",
    "brother": "Her brother plays football.",
    "grandmother": "My grandmother tells interesting stories.",
    "grandfather": "His grandfather lives in the countryside.",
    "parents": "My parents support my studies.",
    "baby": "The baby is sleeping in the next room.",
    "game": "We played a board game after dinner.",
    "movie": "The movie starts at eight.",
    "sport": "Sport helps me feel energetic.",
    "dance": "They learned a new dance together.",
    "photo": "I took a photo of the sunset.",
    "song": "This song is easy to remember.",
    "walk": "We went for a walk after lunch.",
    "reading": "Reading helps me learn new words.",
    "left": "Turn left after the supermarket.",
    "right": "The cafe is on the right.",
    "straight": "Go straight until you see the bridge.",
    "near": "The bus stop is near my house.",
    "far": "The airport is far from the city.",
    "behind": "The parking lot is behind the hotel.",
    "between": "The bank is between the shop and the cafe.",
    "opposite": "The museum is opposite the park.",
    "tram": "The tram stops near the square.",
    "train": "The train leaves at half past six.",
    "flight": "Our flight was delayed by one hour.",
    "platform": "We waited on platform three.",
    "driver": "The driver stopped at the red light.",
    "route": "This route goes through the city center.",
    "delay": "There was a delay because of bad weather.",
    "transfer": "We have a transfer in Berlin.",
    "reception": "Ask at reception if you need help.",
    "reservation": "I made a reservation for two nights.",
    "key": "The receptionist gave us the room key.",
    "elevator": "Take the elevator to the fifth floor.",
    "guest": "Every guest received a welcome drink.",
    "towel": "Could you bring one more towel?",
    "check-in": "Check-in begins at two o'clock.",
    "checkout": "Checkout is before noon.",
    "waiter": "The waiter brought our drinks.",
    "order": "We placed our order quickly.",
    "dish": "This dish is popular with tourists.",
    "fork": "There is no fork on the table.",
    "knife": "Be careful with this sharp knife.",
    "spoon": "I need a spoon for the soup.",
    "taste": "The taste of the sauce was unusual.",
    "spicy": "This food is too spicy for me.",
    "password": "Create a strong password for your account.",
    "website": "The website has useful information.",
    "message": "I sent her a short message.",
    "email": "Please send the document by email.",
    "download": "The download took only a few seconds.",
    "upload": "I need to upload my homework before midnight.",
    "screen": "The screen is too bright at night.",
    "link": "She shared a link to the article.",
    "happy": "He looked happy after the exam.",
    "sad": "She felt sad after saying goodbye.",
    "angry": "The customer was angry about the delay.",
    "tired": "I was tired after a long day.",
    "worried": "They were worried about the results.",
    "calm": "Try to stay calm before the interview.",
    "excited": "The students were excited about the trip.",
    "bored": "He felt bored during the long meeting.",
    "team": "Our team won the match.",
    "player": "The player scored in the final minute.",
    "match": "The match started at seven.",
    "score": "The final score was two to one.",
    "goal": "She scored an important goal.",
    "coach": "The coach explained the plan.",
    "training": "Training starts early tomorrow.",
    "winner": "The winner received a small prize.",
    "forest": "We walked through the forest in the morning.",
    "river": "The river flows through the city.",
    "mountain": "The mountain was covered with snow.",
    "lake": "We swam in the lake last summer.",
    "island": "The island is famous for its beaches.",
    "field": "Children played in the field.",
    "flower": "She put a flower on the table.",
    "tree": "A large tree grows near our house.",
    "clean": "I need to clean my room today.",
    "wash": "Please wash your hands before dinner.",
    "cook": "He likes to cook pasta on weekends.",
    "repair": "We need to repair the old chair.",
    "dust": "There is dust on the bookshelf.",
    "laundry": "I do the laundry every Saturday.",
    "trash": "Take out the trash before you leave.",
    "vacuum": "I vacuum the carpet twice a week.",
    "agenda": "The agenda includes three important questions.",
    "feedback": "The manager gave helpful feedback.",
    "proposal": "She prepared a proposal for the client.",
    "task": "This task must be finished today.",
    "update": "Send me an update after the meeting.",
    "priority": "This project is our main priority.",
    "request": "The client sent a new request.",
    "summary": "I wrote a short summary of the discussion.",
    "client": "The client liked the new design.",
    "budget": "We need to stay within the budget.",
    "profit": "The company increased its profit this year.",
    "contract": "They signed the contract yesterday.",
    "brand": "The brand is popular with young people.",
    "growth": "The business showed steady growth.",
    "strategy": "Their strategy helped them enter a new market.",
    "market": "The company entered a new market last year.",
    "customs": "We had to show our bags at customs.",
    "insurance": "Travel insurance can protect you abroad.",
    "itinerary": "Our itinerary includes three cities.",
    "destination": "Paris is our final destination.",
    "accommodation": "We found cheap accommodation near the station.",
    "cancellation": "The cancellation surprised all passengers.",
    "boarding": "Boarding starts twenty minutes before departure.",
    "departure": "The departure time changed in the app.",
    "exhibition": "The exhibition opened on Friday.",
    "performance": "The performance received a long applause.",
    "audience": "The audience listened carefully.",
    "tradition": "This tradition is important for the local community.",
    "heritage": "The city is proud of its cultural heritage.",
    "festival": "The festival attracts visitors every summer.",
    "sculpture": "The sculpture stands in the main square.",
    "painting": "The painting shows a quiet village.",
    "assignment": "The assignment is due on Monday.",
    "lecture": "The lecture was about modern history.",
    "research": "Her research focuses on language learning.",
    "degree": "He received a degree in economics.",
    "campus": "The campus has a large library.",
    "deadline": "The deadline for the essay is Friday.",
    "grade": "I got a good grade for my essay.",
    "essay": "The essay must include clear arguments.",
    "trust": "Trust is important in any relationship.",
    "support": "Her friends gave her strong support.",
    "argument": "They had an argument about money.",
    "advice": "My teacher gave me useful advice.",
    "neighbor": "My neighbor helped me carry the bags upstairs.",
    "community": "The local community organized a cleanup day.",
    "respect": "Respect makes communication easier.",
    "promise": "He made a promise to call every week.",
    "headline": "The headline caught my attention.",
    "article": "I read an article about climate change.",
    "source": "Always check the source of the information.",
    "broadcast": "The broadcast started at six.",
    "interview": "The interview was published online.",
    "editor": "The editor corrected the article.",
    "channel": "This channel posts daily news.",
    "review": "She wrote a review of the new film.",
    "income": "His income increased after the promotion.",
    "expense": "Rent is my biggest monthly expense.",
    "loan": "They took a loan to buy a car.",
    "account": "I opened a new bank account.",
    "savings": "She keeps her savings in the bank.",
    "payment": "The payment was completed online.",
    "currency": "The local currency is different here.",
    "interest": "The bank pays interest on savings.",
    "pollution": "Air pollution is a serious problem.",
    "recycling": "Recycling helps reduce waste.",
    "waste": "The city wants to produce less waste.",
    "climate": "The climate is changing quickly.",
    "energy": "Solar energy is becoming cheaper.",
    "resource": "Water is an important resource.",
    "emission": "Factories must reduce harmful emissions.",
    "wildlife": "The forest is home to diverse wildlife.",
    "experience": "This trip was an unforgettable experience.",
    "impression": "The city made a strong impression on me.",
    "activity": "Choose an activity you enjoy.",
    "event": "The event will take place on Friday.",
    "recommendation": "I followed my friend's recommendation.",
    "atmosphere": "The cafe has a warm atmosphere.",
    "memory": "This song brings back a happy memory.",
    "entertainment": "The city offers many forms of entertainment.",
    "leadership": "Good leadership helps a team grow.",
    "negotiation": "The negotiation lasted two hours.",
    "expertise": "Her expertise is valuable for the project.",
    "responsibility": "This role comes with great responsibility.",
    "achievement": "Finishing the course was a real achievement.",
    "evaluation": "The evaluation showed strong progress.",
    "initiative": "He showed initiative during the project.",
    "competence": "Professional competence develops with practice.",
    "evidence": "The evidence supports the theory.",
    "experiment": "The experiment produced unexpected results.",
    "hypothesis": "The hypothesis needs more evidence.",
    "discovery": "The discovery changed the direction of the research.",
    "analysis": "The analysis revealed several patterns.",
    "method": "This method is simple and reliable.",
    "sample": "The scientist tested a small sample.",
    "theory": "The theory explains the main results.",
    "regulation": "The new regulation affects online services.",
    "agreement": "The agreement was signed by both companies.",
    "requirement": "Experience is not a strict requirement for this role.",
    "violation": "The company paid a fine for the violation.",
    "permission": "You need permission to enter this area.",
    "liability": "The contract limits the company's liability.",
    "claim": "The customer made a claim about the product.",
    "procedure": "The procedure must be followed carefully.",
    "policy": "The new policy supports remote work.",
    "election": "The election results were announced at night.",
    "citizen": "Every citizen has rights and responsibilities.",
    "debate": "The debate focused on education.",
    "reform": "The reform changed the healthcare system.",
    "campaign": "The campaign encouraged people to vote.",
    "authority": "The local authority approved the plan.",
    "rights": "Human rights must be protected.",
    "behavior": "His behavior changed after the training.",
    "attention": "The task requires full attention.",
    "motivation": "Clear goals can increase motivation.",
    "habit": "Reading every evening became a habit.",
    "perception": "Perception can be influenced by experience.",
    "stress": "Too much stress affects sleep.",
    "confidence": "Practice builds confidence.",
    "interface": "The interface is simple and clear.",
    "workflow": "The new workflow saves time.",
    "integration": "The integration connects two services.",
    "deployment": "Deployment is planned for Friday.",
    "performance": "The update improved performance.",
    "scalability": "Scalability is important for a growing product.",
    "prototype": "The team tested a prototype with users.",
    "release": "The release includes several new features.",
    "abstract": "The abstract summarizes the main idea of the paper.",
    "citation": "Every citation must include a source.",
    "conclusion": "The conclusion answers the research question.",
    "framework": "The framework helps organize the analysis.",
    "relevance": "The relevance of the topic is clear.",
    "limitation": "The study has one important limitation.",
    "relocation": "Relocation to another country can be stressful.",
    "adaptation": "Adaptation takes time and patience.",
    "diversity": "Diversity makes the team stronger.",
    "background": "Her background includes marketing and design.",
    "fluency": "Fluency improves with regular speaking practice.",
    "expectation": "The result met our expectation.",
    "boundary": "It is important to set a healthy boundary.",
    "opportunity": "The internship is a great opportunity.",
}


def build_extra_word_sets() -> list[dict]:
    return [
        {
            "code": code,
            "title": title,
            "level": level,
            "description": description,
            "cards": [
                (
                    foreign_word,
                    translation,
                    EXTRA_WORD_EXAMPLES.get(
                        foreign_word,
                        f"I used {foreign_word} in a real conversation.",
                    ),
                )
                for foreign_word, translation in cards
            ],
        }
        for code, title, level, description, cards in EXTRA_WORD_SET_BLUEPRINTS
    ]


DEFAULT_WORD_SETS.extend(build_extra_word_sets())

SPANISH_WORDS = {
    "ticket": "boleto", "airport": "aeropuerto", "hotel": "hotel", "map": "mapa", "passport": "pasaporte", "station": "estación", "luggage": "equipaje", "guide": "guía",
    "friend": "amigo", "work": "trabajo", "family": "familia", "evening": "tarde", "morning": "mañana", "street": "calle", "window": "ventana", "phone": "teléfono",
    "menu": "menú", "breakfast": "desayuno", "water": "agua", "bill": "cuenta", "dessert": "postre", "soup": "sopa", "coffee": "café", "plate": "plato",
    "lesson": "lección", "teacher": "profesor", "student": "estudiante", "homework": "tarea", "notebook": "cuaderno", "library": "biblioteca", "exam": "examen", "question": "pregunta",
    "bridge": "puente", "square": "plaza", "museum": "museo", "park": "parque", "corner": "esquina", "traffic": "tráfico", "avenue": "avenida", "building": "edificio",
    "price": "precio", "cash": "efectivo", "receipt": "recibo", "size": "talla", "store": "tienda", "discount": "descuento", "bag": "bolsa", "card": "tarjeta",
    "meeting": "reunión", "deadline": "plazo", "manager": "gerente", "salary": "salario", "interview": "entrevista", "colleague": "colega", "report": "informe", "career": "carrera",
    "headache": "dolor de cabeza", "medicine": "medicina", "appointment": "cita", "treatment": "tratamiento", "exercise": "ejercicio", "fever": "fiebre", "symptom": "síntoma", "injury": "lesión",
    "device": "dispositivo", "security": "seguridad", "software": "software", "database": "base de datos", "feature": "función", "account": "cuenta", "network": "red", "backup": "copia de seguridad",
}

ITALIAN_WORDS = {
    "ticket": "biglietto", "airport": "aeroporto", "hotel": "hotel", "map": "mappa", "passport": "passaporto", "station": "stazione", "luggage": "bagaglio", "guide": "guida",
    "friend": "amico", "work": "lavoro", "family": "famiglia", "evening": "sera", "morning": "mattina", "street": "strada", "window": "finestra", "phone": "telefono",
    "menu": "menù", "breakfast": "colazione", "water": "acqua", "bill": "conto", "dessert": "dolce", "soup": "zuppa", "coffee": "caffè", "plate": "piatto",
    "lesson": "lezione", "teacher": "insegnante", "student": "studente", "homework": "compito", "notebook": "quaderno", "library": "biblioteca", "exam": "esame", "question": "domanda",
    "bridge": "ponte", "square": "piazza", "museum": "museo", "park": "parco", "corner": "angolo", "traffic": "traffico", "avenue": "viale", "building": "edificio",
    "price": "prezzo", "cash": "contanti", "receipt": "scontrino", "size": "taglia", "store": "negozio", "discount": "sconto", "bag": "borsa", "card": "carta",
    "meeting": "riunione", "deadline": "scadenza", "manager": "responsabile", "salary": "stipendio", "interview": "colloquio", "colleague": "collega", "report": "rapporto", "career": "carriera",
    "headache": "mal di testa", "medicine": "medicina", "appointment": "appuntamento", "treatment": "trattamento", "exercise": "esercizio", "fever": "febbre", "symptom": "sintomo", "injury": "infortunio",
    "device": "dispositivo", "security": "sicurezza", "software": "software", "database": "database", "feature": "funzione", "account": "account", "network": "rete", "backup": "backup",
}

SPANISH_WORDS.update({
    "abstract": "resumen", "access": "acceso", "accommodation": "alojamiento", "achievement": "logro", "activity": "actividad", "adaptation": "adaptación", "advice": "consejo", "agenda": "agenda",
    "agreement": "acuerdo", "analysis": "análisis", "angry": "enojado", "answer": "respuesta", "apple": "manzana", "argument": "argumento", "article": "artículo", "assignment": "tarea",
    "atmosphere": "ambiente", "attention": "atención", "audience": "público", "authority": "autoridad", "baby": "bebé", "background": "origen", "bathroom": "baño", "bed": "cama",
    "behavior": "comportamiento", "behind": "detrás", "between": "entre", "bird": "pájaro", "board": "pizarra", "boarding": "embarque", "book": "libro", "bored": "aburrido",
    "boundary": "límite", "boy": "niño", "brand": "marca", "bread": "pan", "broadcast": "transmisión", "brother": "hermano", "budget": "presupuesto", "bus": "autobús",
    "calm": "tranquilo", "campaign": "campaña", "campus": "campus", "cancellation": "cancelación", "cat": "gato", "chair": "silla", "channel": "canal", "check-in": "registro",
    "checkout": "salida", "child": "niño", "citation": "cita", "citizen": "ciudadano", "claim": "reclamo", "class": "clase", "clean": "limpiar", "client": "cliente",
    "climate": "clima", "clinic": "clínica", "cloud": "nube", "coach": "entrenador", "coat": "abrigo", "cold": "frío", "community": "comunidad", "competence": "competencia",
    "conclusion": "conclusión", "confidence": "confianza", "contract": "contrato", "cook": "cocinar", "cow": "vaca", "crosswalk": "paso de peatones", "currency": "moneda", "customer": "cliente",
    "customs": "aduana", "dance": "baile", "day": "día", "debate": "debate", "degree": "título", "delay": "retraso", "department": "departamento", "departure": "salida",
    "deployment": "despliegue", "desk": "escritorio", "destination": "destino", "diet": "dieta", "discovery": "descubrimiento", "dish": "plato", "district": "distrito", "diversity": "diversidad",
    "dog": "perro", "door": "puerta", "download": "descarga", "dress": "vestido", "driver": "conductor", "dust": "polvo", "editor": "editor", "election": "elección",
    "elevator": "ascensor", "email": "correo electrónico", "emission": "emisión", "energy": "energía", "entertainment": "entretenimiento", "essay": "ensayo", "evaluation": "evaluación", "event": "evento",
    "evidence": "evidencia", "excited": "emocionado", "exhibition": "exposición", "expectation": "expectativa", "expense": "gasto", "experience": "experiencia", "experiment": "experimento", "expertise": "experiencia profesional",
    "eyes": "ojos", "far": "lejos", "father": "padre", "feedback": "retroalimentación", "festival": "festival", "field": "campo", "fish": "pez", "flight": "vuelo",
    "floor": "suelo", "flower": "flor", "fluency": "fluidez", "forest": "bosque", "fork": "tenedor", "fountain": "fuente", "framework": "marco", "game": "juego",
    "girl": "niña", "goal": "gol", "grade": "nota", "grandfather": "abuelo", "grandmother": "abuela", "growth": "crecimiento", "guest": "huésped", "habit": "hábito",
    "hair": "pelo", "happy": "feliz", "hat": "sombrero", "headline": "titular", "heritage": "patrimonio", "horse": "caballo", "hot": "calor", "hour": "hora",
    "hypothesis": "hipótesis", "impression": "impresión", "income": "ingreso", "initiative": "iniciativa", "insurance": "seguro", "integration": "integración", "interest": "interés", "interface": "interfaz",
    "island": "isla", "itinerary": "itinerario", "jacket": "chaqueta", "key": "llave", "kitchen": "cocina", "knife": "cuchillo", "lake": "lago", "lamp": "lámpara",
    "laundry": "lavandería", "leadership": "liderazgo", "lecture": "conferencia", "left": "izquierda", "liability": "responsabilidad legal", "limitation": "limitación", "link": "enlace", "loan": "préstamo",
    "man": "hombre", "match": "partido", "memory": "memoria", "message": "mensaje", "method": "método", "minute": "minuto", "mirror": "espejo", "month": "mes",
    "market": "mercado",
    "mother": "madre", "motivation": "motivación", "mountain": "montaña", "mouse": "ratón", "movie": "película", "music": "música", "near": "cerca", "negotiation": "negociación",
    "neighbor": "vecino", "opportunity": "oportunidad", "opposite": "enfrente", "order": "pedido", "page": "página", "pain": "dolor", "painting": "cuadro", "pants": "pantalones",
    "parents": "padres", "password": "contraseña", "payment": "pago", "pen": "bolígrafo", "pencil": "lápiz", "perception": "percepción", "performance": "actuación", "permission": "permiso",
    "photo": "foto", "platform": "plataforma", "player": "jugador", "policy": "política", "pollution": "contaminación", "priority": "prioridad", "privacy": "privacidad", "procedure": "procedimiento",
    "profit": "beneficio", "project": "proyecto", "promise": "promesa", "promotion": "ascenso", "proposal": "propuesta", "prototype": "prototipo", "rabbit": "conejo", "rain": "lluvia",
    "reading": "lectura", "reception": "recepción", "recommendation": "recomendación", "recovery": "recuperación", "recycling": "reciclaje", "reform": "reforma", "regulation": "regulación", "release": "lanzamiento",
    "relevance": "relevancia", "relocation": "reubicación", "repair": "reparar", "request": "solicitud", "requirement": "requisito", "research": "investigación", "reservation": "reserva", "resource": "recurso",
    "respect": "respeto", "responsibility": "responsabilidad", "review": "reseña", "right": "derecha", "rights": "derechos", "river": "río", "room": "habitación", "route": "ruta",
    "sad": "triste", "salad": "ensalada", "sample": "muestra", "savings": "ahorros", "scalability": "escalabilidad", "schedule": "horario", "score": "marcador", "screen": "pantalla",
    "sculpture": "escultura", "shelf": "estante", "shirt": "camisa", "shoes": "zapatos", "sister": "hermana", "skirt": "falda", "smile": "sonrisa", "snow": "nieve",
    "sofa": "sofá", "song": "canción", "source": "fuente", "spicy": "picante", "spoon": "cuchara", "sport": "deporte", "straight": "recto", "strategy": "estrategia",
    "stress": "estrés", "subject": "asignatura", "subway": "metro", "summary": "resumen", "sun": "sol", "support": "apoyo", "sweater": "suéter", "table": "mesa",
    "task": "tarea", "taste": "sabor", "taxi": "taxi", "tea": "té", "team": "equipo", "theory": "teoría", "tired": "cansado", "today": "hoy",
    "tomorrow": "mañana", "towel": "toalla", "tradition": "tradición", "train": "tren", "training": "entrenamiento", "tram": "tranvía", "transfer": "transbordo", "trash": "basura",
    "tree": "árbol", "trip": "viaje", "trust": "confianza", "update": "actualización", "upgrade": "mejora", "upload": "subida", "vacancy": "vacante", "vacuum": "aspirar",
    "violation": "infracción", "waiter": "camarero", "walk": "paseo", "wall": "pared", "warm": "cálido", "wash": "lavar", "waste": "residuo", "website": "sitio web",
    "week": "semana", "wildlife": "fauna silvestre", "wind": "viento", "winner": "ganador", "woman": "mujer", "workflow": "flujo de trabajo", "worried": "preocupado", "year": "año",
})

ITALIAN_WORDS.update({
    "abstract": "abstract", "access": "accesso", "accommodation": "alloggio", "achievement": "risultato", "activity": "attività", "adaptation": "adattamento", "advice": "consiglio", "agenda": "ordine del giorno",
    "agreement": "accordo", "analysis": "analisi", "angry": "arrabbiato", "answer": "risposta", "apple": "mela", "argument": "argomento", "article": "articolo", "assignment": "compito",
    "atmosphere": "atmosfera", "attention": "attenzione", "audience": "pubblico", "authority": "autorità", "baby": "bambino", "background": "esperienza", "bathroom": "bagno", "bed": "letto",
    "behavior": "comportamento", "behind": "dietro", "between": "tra", "bird": "uccello", "board": "lavagna", "boarding": "imbarco", "book": "libro", "bored": "annoiato",
    "boundary": "confine", "boy": "ragazzo", "brand": "marchio", "bread": "pane", "broadcast": "trasmissione", "brother": "fratello", "budget": "budget", "bus": "autobus",
    "calm": "calmo", "campaign": "campagna", "campus": "campus", "cancellation": "cancellazione", "cat": "gatto", "chair": "sedia", "channel": "canale", "check-in": "check-in",
    "checkout": "check-out", "child": "bambino", "citation": "citazione", "citizen": "cittadino", "claim": "reclamo", "class": "classe", "clean": "pulire", "client": "cliente",
    "climate": "clima", "clinic": "clinica", "cloud": "nuvola", "coach": "allenatore", "coat": "cappotto", "cold": "freddo", "community": "comunità", "competence": "competenza",
    "conclusion": "conclusione", "confidence": "fiducia", "contract": "contratto", "cook": "cucinare", "cow": "mucca", "crosswalk": "strisce pedonali", "currency": "valuta", "customer": "cliente",
    "customs": "dogana", "dance": "danza", "day": "giorno", "debate": "dibattito", "degree": "laurea", "delay": "ritardo", "department": "reparto", "departure": "partenza",
    "deployment": "distribuzione", "desk": "scrivania", "destination": "destinazione", "diet": "dieta", "discovery": "scoperta", "dish": "piatto", "district": "quartiere", "diversity": "diversità",
    "dog": "cane", "door": "porta", "download": "download", "dress": "vestito", "driver": "autista", "dust": "polvere", "editor": "redattore", "election": "elezione",
    "elevator": "ascensore", "email": "email", "emission": "emissione", "energy": "energia", "entertainment": "intrattenimento", "essay": "saggio", "evaluation": "valutazione", "event": "evento",
    "evidence": "prova", "excited": "emozionato", "exhibition": "mostra", "expectation": "aspettativa", "expense": "spesa", "experience": "esperienza", "experiment": "esperimento", "expertise": "competenza specialistica",
    "eyes": "occhi", "far": "lontano", "father": "padre", "feedback": "feedback", "festival": "festival", "field": "campo", "fish": "pesce", "flight": "volo",
    "floor": "pavimento", "flower": "fiore", "fluency": "fluidità", "forest": "foresta", "fork": "forchetta", "fountain": "fontana", "framework": "struttura", "game": "gioco",
    "girl": "ragazza", "goal": "gol", "grade": "voto", "grandfather": "nonno", "grandmother": "nonna", "growth": "crescita", "guest": "ospite", "habit": "abitudine",
    "hair": "capelli", "happy": "felice", "hat": "cappello", "headline": "titolo", "heritage": "patrimonio", "horse": "cavallo", "hot": "caldo", "hour": "ora",
    "hypothesis": "ipotesi", "impression": "impressione", "income": "reddito", "initiative": "iniziativa", "insurance": "assicurazione", "integration": "integrazione", "interest": "interesse", "interface": "interfaccia",
    "island": "isola", "itinerary": "itinerario", "jacket": "giacca", "key": "chiave", "kitchen": "cucina", "knife": "coltello", "lake": "lago", "lamp": "lampada",
    "laundry": "bucato", "leadership": "leadership", "lecture": "lezione universitaria", "left": "sinistra", "liability": "responsabilità legale", "limitation": "limitazione", "link": "collegamento", "loan": "prestito",
    "man": "uomo", "match": "partita", "memory": "memoria", "message": "messaggio", "method": "metodo", "minute": "minuto", "mirror": "specchio", "month": "mese",
    "market": "mercato",
    "mother": "madre", "motivation": "motivazione", "mountain": "montagna", "mouse": "topo", "movie": "film", "music": "musica", "near": "vicino", "negotiation": "negoziazione",
    "neighbor": "vicino", "opportunity": "opportunità", "opposite": "di fronte", "order": "ordine", "page": "pagina", "pain": "dolore", "painting": "dipinto", "pants": "pantaloni",
    "parents": "genitori", "password": "password", "payment": "pagamento", "pen": "penna", "pencil": "matita", "perception": "percezione", "performance": "prestazione", "permission": "permesso",
    "photo": "foto", "platform": "piattaforma", "player": "giocatore", "policy": "politica", "pollution": "inquinamento", "priority": "priorità", "privacy": "privacy", "procedure": "procedura",
    "profit": "profitto", "project": "progetto", "promise": "promessa", "promotion": "promozione", "proposal": "proposta", "prototype": "prototipo", "rabbit": "coniglio", "rain": "pioggia",
    "reading": "lettura", "reception": "reception", "recommendation": "raccomandazione", "recovery": "recupero", "recycling": "riciclaggio", "reform": "riforma", "regulation": "regolamento", "release": "rilascio",
    "relevance": "rilevanza", "relocation": "trasferimento", "repair": "riparare", "request": "richiesta", "requirement": "requisito", "research": "ricerca", "reservation": "prenotazione", "resource": "risorsa",
    "respect": "rispetto", "responsibility": "responsabilità", "review": "recensione", "right": "destra", "rights": "diritti", "river": "fiume", "room": "camera", "route": "percorso",
    "sad": "triste", "salad": "insalata", "sample": "campione", "savings": "risparmi", "scalability": "scalabilità", "schedule": "orario", "score": "punteggio", "screen": "schermo",
    "sculpture": "scultura", "shelf": "scaffale", "shirt": "camicia", "shoes": "scarpe", "sister": "sorella", "skirt": "gonna", "smile": "sorriso", "snow": "neve",
    "sofa": "divano", "song": "canzone", "source": "fonte", "spicy": "piccante", "spoon": "cucchiaio", "sport": "sport", "straight": "dritto", "strategy": "strategia",
    "stress": "stress", "subject": "materia", "subway": "metropolitana", "summary": "riassunto", "sun": "sole", "support": "supporto", "sweater": "maglione", "table": "tavolo",
    "task": "compito", "taste": "gusto", "taxi": "taxi", "tea": "tè", "team": "squadra", "theory": "teoria", "tired": "stanco", "today": "oggi",
    "tomorrow": "domani", "towel": "asciugamano", "tradition": "tradizione", "train": "treno", "training": "allenamento", "tram": "tram", "transfer": "cambio", "trash": "spazzatura",
    "tree": "albero", "trip": "viaggio", "trust": "fiducia", "update": "aggiornamento", "upgrade": "miglioramento", "upload": "caricamento", "vacancy": "posto vacante", "vacuum": "passare l'aspirapolvere",
    "violation": "violazione", "waiter": "cameriere", "walk": "passeggiata", "wall": "parete", "warm": "caldo", "wash": "lavare", "waste": "rifiuti", "website": "sito web",
    "week": "settimana", "wildlife": "fauna selvatica", "wind": "vento", "winner": "vincitore", "woman": "donna", "workflow": "flusso di lavoro", "worried": "preoccupato", "year": "anno",
})


def translate_foreign_word(language: str, english_word: str) -> str:
    if language == "Spanish":
        return SPANISH_WORDS.get(english_word, f"{english_word} en español")
    if language == "Italian":
        return ITALIAN_WORDS.get(english_word, f"{english_word} in italiano")
    return english_word


def get_language_prefix(language: str) -> str:
    return LANGUAGE_CODE_PREFIX.get(language, "en")


def build_custom_word_set_code(language: str) -> str:
    return f"{CUSTOM_WORD_SET_CODE}_{get_language_prefix(language)}"


def build_special_word_set_code(language: str, set_code: str) -> str:
    return f"{get_language_prefix(language)}_{set_code}"


def get_user_language(session: Session, telegram_id: int) -> str:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None or user.current_language not in SUPPORTED_LANGUAGES:
        return "English"
    return user.current_language


def build_language_example(language: str, foreign_word: str, original_example: str) -> str:
    if language == "English":
        return original_example
    return LANGUAGE_EXAMPLE_TEMPLATES[language].format(word=foreign_word)


def localize_word_set(word_set_data: dict, language: str) -> dict:
    if language == "English":
        return {
            **word_set_data,
            "language": "English",
            "code": word_set_data["code"],
        }

    prefix = LANGUAGE_CODE_PREFIX[language]
    return {
        **word_set_data,
        "language": language,
        "code": f"{prefix}_{word_set_data['code']}",
        "title": f"{word_set_data['title']} — {SUPPORTED_LANGUAGES[language]}",
        "description": f"{word_set_data['description']} Язык: {SUPPORTED_LANGUAGES[language].lower()}.",
        "cards": [
            (
                translate_foreign_word(language, foreign_word),
                translation,
                build_language_example(
                    language,
                    translate_foreign_word(language, foreign_word),
                    example,
                ),
            )
            for foreign_word, translation, example in word_set_data["cards"]
        ],
    }


BASE_WORD_SETS = DEFAULT_WORD_SETS
DEFAULT_WORD_SETS = [
    localize_word_set(word_set_data, language)
    for language in SUPPORTED_LANGUAGES
    for word_set_data in BASE_WORD_SETS
]

LEVEL_ORDER = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
}

ORDER_TO_LEVEL = {order: level for level, order in LEVEL_ORDER.items()}


@dataclass(slots=True)
class RecommendedCard:
    set_code: str
    position: int
    reason: str


@dataclass(slots=True)
class WordSetView:
    code: str
    title: str
    level: str
    description: str
    cards_count: int
    recommended_position: int
    recommendation_reason: str


@dataclass(slots=True)
class QuizQuestion:
    set_code: str
    set_title: str
    position: int
    total: int
    word_card_id: int
    foreign_word: str
    correct_translation: str
    options: list[str]


@dataclass(slots=True)
class ProgressStats:
    total_attempts: int
    total_questions: int
    total_correct: int
    best_result: int
    saved_words_count: int
    today_attempts: int = 0
    weak_words_count: int = 0
    strongest_set_title: str | None = None
    weakest_set_title: str | None = None

    @property
    def accuracy_percent(self) -> int:
        if self.total_questions == 0:
            return 0
        return round((self.total_correct / self.total_questions) * 100)


def seed_learning_content(session: Session) -> None:
    valid_codes = {word_set_data["code"] for word_set_data in DEFAULT_WORD_SETS}
    valid_codes.update(
        build_special_word_set_code(language, code)
        for language in SUPPORTED_LANGUAGES
        for code, _ in SPECIAL_WORD_SETS
    )
    valid_codes.update(
        build_custom_word_set_code(language)
        for language in SUPPORTED_LANGUAGES
    )
    existing_sets = list(session.scalars(select(WordSet)))
    obsolete_sets = [
        word_set
        for word_set in existing_sets
        if word_set.is_system and word_set.code not in valid_codes
    ]

    for obsolete_set in obsolete_sets:
        obsolete_card_ids = list(
            session.scalars(
                select(WordCard.id).where(WordCard.word_set_id == obsolete_set.id)
            )
        )
        if obsolete_card_ids:
            session.execute(
                delete(UserWord).where(UserWord.word_card_id.in_(obsolete_card_ids))
            )
            session.execute(
                delete(UserWordProgress).where(
                    UserWordProgress.word_card_id.in_(obsolete_card_ids)
                )
            )
            session.execute(
                delete(WordCard).where(WordCard.id.in_(obsolete_card_ids))
            )
        session.execute(
            delete(QuizAttempt).where(QuizAttempt.word_set_id == obsolete_set.id)
        )
        session.delete(obsolete_set)

    for word_set_data in DEFAULT_WORD_SETS:
        word_set = session.scalar(select(WordSet).where(WordSet.code == word_set_data["code"]))
        if word_set is None:
            word_set = WordSet(
                code=word_set_data["code"],
                title=word_set_data["title"],
                language=word_set_data["language"],
                level=word_set_data["level"],
                description=word_set_data["description"],
                is_system=True,
            )
            session.add(word_set)
            session.flush()
        else:
            word_set.title = word_set_data["title"]
            word_set.language = word_set_data["language"]
            word_set.level = word_set_data["level"]
            word_set.description = word_set_data["description"]
            word_set.is_system = True

        for index, (foreign_word, translation, example) in enumerate(
            word_set_data["cards"],
            start=1,
        ):
            card = session.scalar(
                select(WordCard).where(
                    WordCard.word_set_id == word_set.id,
                    WordCard.position == index,
                )
            )
            if card is None:
                session.add(
                    WordCard(
                        word_set_id=word_set.id,
                        position=index,
                        foreign_word=foreign_word,
                        translation=translation,
                        example=example,
                    )
                )
            else:
                card.foreign_word = foreign_word
                card.translation = translation
                card.example = example

    session.flush()

    for language in SUPPORTED_LANGUAGES:
        custom_word_set = session.scalar(
            select(WordSet).where(WordSet.code == build_custom_word_set_code(language))
        )
        if custom_word_set is not None:
            custom_word_set.language = language
            custom_word_set.is_system = False

        for code, title in SPECIAL_WORD_SETS:
            special_code = build_special_word_set_code(language, code)
            word_set = session.scalar(select(WordSet).where(WordSet.code == special_code))
            if word_set is None:
                session.add(
                    WordSet(
                        code=special_code,
                        title=f"{title} — {SUPPORTED_LANGUAGES[language]}",
                        language=language,
                        level="A1",
                        description="Служебный набор для учета статистики.",
                        is_system=False,
                    )
                )
            else:
                word_set.title = f"{title} — {SUPPORTED_LANGUAGES[language]}"
                word_set.language = language
                word_set.description = "Служебный набор для учета статистики."
                word_set.is_system = False

    session.flush()


def get_or_create_custom_word_set(session: Session, language: str) -> WordSet:
    code = build_custom_word_set_code(language)
    word_set = session.scalar(select(WordSet).where(WordSet.code == code))
    if word_set is not None:
        word_set.language = language
        word_set.is_system = False
        return word_set

    word_set = WordSet(
        code=code,
        title=f"Мои слова — {SUPPORTED_LANGUAGES[language]}",
        language=language,
        level="A1",
        description="Пользовательские слова, добавленные вручную.",
        is_system=False,
    )
    session.add(word_set)
    session.flush()
    return word_set


def get_word_sets(session: Session, telegram_id: int) -> list[WordSetView]:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    user_level = user.level if user is not None else "A1"
    user_language = get_user_language(session, telegram_id)
    max_level_order = LEVEL_ORDER.get(user_level, 1)

    statement: Select[tuple[WordSet]] = (
        select(WordSet)
        .options(joinedload(WordSet.cards))
        .where(WordSet.is_system.is_(True), WordSet.language == user_language)
        .order_by(WordSet.level, WordSet.id)
    )
    word_sets = [
        word_set
        for word_set in session.scalars(statement).unique()
        if LEVEL_ORDER.get(word_set.level, 1) <= max_level_order
    ]

    result = []
    for word_set in word_sets:
        recommendation = recommend_card_for_user(session, telegram_id, word_set)
        result.append(
            WordSetView(
                code=word_set.code,
                title=word_set.title,
                level=word_set.level,
                description=word_set.description,
                cards_count=len(word_set.cards),
                recommended_position=recommendation.position,
                recommendation_reason=recommendation.reason,
            )
        )
    return result


def get_next_level(current_level: str) -> str | None:
    next_order = LEVEL_ORDER.get(current_level, 1) + 1
    return ORDER_TO_LEVEL.get(next_order)


def get_challenge_word_sets(session: Session, telegram_id: int) -> tuple[str | None, list[WordSetView]]:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    user_level = user.level if user is not None else "A1"
    user_language = get_user_language(session, telegram_id)
    next_level = get_next_level(user_level)
    if next_level is None:
        return None, []

    statement: Select[tuple[WordSet]] = (
        select(WordSet)
        .options(joinedload(WordSet.cards))
        .where(WordSet.level == next_level)
        .where(WordSet.is_system.is_(True))
        .where(WordSet.language == user_language)
        .order_by(WordSet.id)
    )

    result = []
    for word_set in session.scalars(statement).unique():
        recommendation = recommend_card_for_user(session, telegram_id, word_set)
        result.append(
            WordSetView(
                code=word_set.code,
                title=word_set.title,
                level=word_set.level,
                description=word_set.description,
                cards_count=len(word_set.cards),
                recommended_position=recommendation.position,
                recommendation_reason=recommendation.reason,
            )
        )
    return next_level, result


def get_word_set_level(session: Session, set_code: str) -> str | None:
    return session.scalar(select(WordSet.level).where(WordSet.code == set_code))


def get_word_set_by_code(session: Session, code: str) -> WordSet | None:
    statement = (
        select(WordSet)
        .options(joinedload(WordSet.cards))
        .where(WordSet.code == code)
    )
    return session.scalar(statement)


def get_card_by_position(
    session: Session,
    set_code: str,
    position: int,
    telegram_id: int | None = None,
) -> tuple[WordSet, WordCard] | None:
    word_set = get_word_set_by_code(session, set_code)
    if word_set is None:
        return None
    if telegram_id is not None and word_set.language != get_user_language(session, telegram_id):
        return None

    cards = sorted(word_set.cards, key=lambda card: card.position)
    if position < 1 or position > len(cards):
        return None

    return word_set, cards[position - 1]


def recommend_card_for_user(session: Session, telegram_id: int, word_set: WordSet) -> RecommendedCard:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    cards = sorted(word_set.cards, key=lambda card: card.position)
    if user is None or not cards:
        return RecommendedCard(word_set.code, 1, "первая карточка")

    progress_rows = list(
        session.execute(
            select(UserWordProgress).where(
                UserWordProgress.user_id == user.id,
                UserWordProgress.word_card_id.in_([card.id for card in cards]),
            )
        ).scalars()
    )
    progress_by_card_id = {row.word_card_id: row for row in progress_rows}

    weak_cards = []
    unseen_cards = []
    for card in cards:
        progress = progress_by_card_id.get(card.id)
        if progress is None or progress.attempts == 0:
            unseen_cards.append(card)
            continue

        accuracy = progress.correct_answers / progress.attempts if progress.attempts else 0
        if accuracy < 0.6 or progress.last_result is False:
            weak_cards.append((accuracy, progress.attempts, card))

    if weak_cards:
        weak_cards.sort(key=lambda item: (item[0], -item[1], item[2].position))
        top_weak_cards = [item[2] for item in weak_cards[: min(3, len(weak_cards))]]
        chosen = random.choice(top_weak_cards)
        return RecommendedCard(word_set.code, chosen.position, "рекомендуем повторить")

    if unseen_cards:
        chosen = random.choice(unseen_cards)
        return RecommendedCard(word_set.code, chosen.position, "новая карточка")

    chosen = random.choice(cards)
    return RecommendedCard(word_set.code, chosen.position, "случайная карточка")


def save_word_for_user(session: Session, telegram_id: int, word_card_id: int) -> bool:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False

    card_language = session.scalar(
        select(WordSet.language)
        .join(WordCard, WordCard.word_set_id == WordSet.id)
        .where(WordCard.id == word_card_id)
    )
    if card_language != get_user_language(session, telegram_id):
        return False

    existing = session.scalar(
        select(UserWord).where(
            UserWord.user_id == user.id,
            UserWord.word_card_id == word_card_id,
        )
    )
    if existing is not None:
        return False

    session.add(UserWord(user_id=user.id, word_card_id=word_card_id))
    session.flush()
    return True


def create_custom_word_for_user(
    session: Session,
    telegram_id: int,
    foreign_word: str,
    translation: str,
    example: str,
) -> bool:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False

    language = get_user_language(session, telegram_id)
    word_set = get_or_create_custom_word_set(session, language)
    next_position = (
        session.scalar(
            select(func.coalesce(func.max(WordCard.position), 0)).where(
                WordCard.word_set_id == word_set.id
            )
        )
        or 0
    ) + 1
    card = WordCard(
        word_set_id=word_set.id,
        position=next_position,
        foreign_word=foreign_word.strip(),
        translation=translation.strip(),
        example=example.strip() or f"I want to remember the word {foreign_word.strip()}.",
    )
    session.add(card)
    session.flush()
    session.add(UserWord(user_id=user.id, word_card_id=card.id))
    session.flush()
    return True


def remove_word_for_user(session: Session, telegram_id: int, word_card_id: int) -> bool:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False

    saved_word = session.scalar(
        select(UserWord).where(
            UserWord.user_id == user.id,
            UserWord.word_card_id == word_card_id,
        )
    )
    if saved_word is None:
        return False

    session.delete(saved_word)
    session.flush()
    return True


def get_user_saved_cards(session: Session, telegram_id: int) -> list[WordCard]:
    language = get_user_language(session, telegram_id)
    statement = (
        select(WordCard)
        .join(WordSet, WordSet.id == WordCard.word_set_id)
        .join(UserWord, UserWord.word_card_id == WordCard.id)
        .join(User, User.id == UserWord.user_id)
        .where(User.telegram_id == telegram_id)
        .where(WordSet.language == language)
        .order_by(UserWord.created_at, WordCard.id)
    )
    return list(session.scalars(statement))


def get_dictionary_card_by_position(
    session: Session,
    telegram_id: int,
    position: int,
) -> WordCard | None:
    cards = get_user_saved_cards(session, telegram_id)
    if position < 1 or position > len(cards):
        return None
    return cards[position - 1]


def build_quiz_question(
    session: Session,
    set_code: str,
    position: int,
    telegram_id: int | None = None,
) -> QuizQuestion | None:
    word_set = get_word_set_by_code(session, set_code)
    if word_set is None:
        return None
    if telegram_id is not None and word_set.language != get_user_language(session, telegram_id):
        return None

    cards = sorted(word_set.cards, key=lambda card: card.position)
    if position < 1 or position > len(cards):
        return None

    current_card = cards[position - 1]
    question_random = random.Random(f"{set_code}:{position}:{current_card.id}")
    all_translations = [card.translation for card in cards if card.id != current_card.id]
    distractors = question_random.sample(all_translations, k=min(3, len(all_translations)))
    while len(distractors) < 3:
        distractors.append(f"Вариант {len(distractors) + 1}")

    options = distractors + [current_card.translation]
    question_random.shuffle(options)

    return QuizQuestion(
        set_code=word_set.code,
        set_title=word_set.title,
        position=position,
        total=len(cards),
        word_card_id=current_card.id,
        foreign_word=current_card.foreign_word,
        correct_translation=current_card.translation,
        options=options,
    )


def get_random_daily_word_set(session: Session, telegram_id: int) -> WordSetView | None:
    word_sets = get_word_sets(session, telegram_id)
    if not word_sets:
        return None
    return random.choice(word_sets)


def get_weak_word_cards(session: Session, telegram_id: int, limit: int = 10) -> list[WordCard]:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return []
    language = get_user_language(session, telegram_id)

    rows = session.execute(
        select(WordCard, UserWordProgress)
        .join(WordSet, WordSet.id == WordCard.word_set_id)
        .join(UserWordProgress, UserWordProgress.word_card_id == WordCard.id)
        .where(
            UserWordProgress.user_id == user.id,
            UserWordProgress.attempts > 0,
            WordSet.language == language,
        )
    ).all()

    weak_rows = []
    seen_words = set()
    for card, progress in rows:
        normalized_word = card.foreign_word.strip().lower()
        if normalized_word in seen_words:
            continue
        accuracy = progress.correct_answers / progress.attempts if progress.attempts else 0
        if progress.last_result is False or progress.correct_answers == 0:
            seen_words.add(normalized_word)
            weak_rows.append((accuracy, -progress.attempts, card.position, card))

    weak_rows.sort(key=lambda item: (item[0], item[1], item[2]))
    return [item[3] for item in weak_rows[:limit]]


def build_weak_quiz_question(
    session: Session,
    telegram_id: int,
    position: int,
    word_card_ids: list[int] | None = None,
) -> QuizQuestion | None:
    if word_card_ids is None:
        weak_cards = get_weak_word_cards(session, telegram_id)
    else:
        language = get_user_language(session, telegram_id)
        cards_by_id = {
            card.id: card
            for card in session.scalars(
                select(WordCard)
                .join(WordSet, WordSet.id == WordCard.word_set_id)
                .where(WordCard.id.in_(word_card_ids), WordSet.language == language)
            )
        }
        weak_cards = [
            cards_by_id[word_card_id]
            for word_card_id in word_card_ids
            if word_card_id in cards_by_id
        ]

    if position < 1 or position > len(weak_cards):
        return None

    current_card = weak_cards[position - 1]
    language = get_user_language(session, telegram_id)
    question_random = random.Random(f"weak:{telegram_id}:{position}:{current_card.id}")
    all_translations = list(
        session.scalars(
            select(WordCard.translation)
            .join(WordSet, WordSet.id == WordCard.word_set_id)
            .where(
                WordSet.is_system.is_(True),
                WordSet.language == language,
                WordCard.id != current_card.id,
            )
        )
    )
    distractors = question_random.sample(all_translations, k=min(3, len(all_translations)))
    while len(distractors) < 3:
        distractors.append(f"Вариант {len(distractors) + 1}")

    options = distractors + [current_card.translation]
    question_random.shuffle(options)
    return QuizQuestion(
        set_code="weak",
        set_title="Повторение ошибок",
        position=position,
        total=len(weak_cards),
        word_card_id=current_card.id,
        foreign_word=current_card.foreign_word,
        correct_translation=current_card.translation,
        options=options,
    )


def get_survival_word_cards(session: Session, telegram_id: int) -> list[WordCard]:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    user_level = user.level if user is not None else "A1"
    user_language = get_user_language(session, telegram_id)
    max_level_order = LEVEL_ORDER.get(user_level, 1)

    rows = session.execute(
        select(WordCard, WordSet)
        .join(WordSet, WordSet.id == WordCard.word_set_id)
        .where(WordSet.is_system.is_(True), WordSet.language == user_language)
    ).all()

    cards = [
        card
        for card, word_set in rows
        if LEVEL_ORDER.get(word_set.level, 1) <= max_level_order
    ]
    random.shuffle(cards)
    return cards


def build_survival_quiz_question(
    session: Session,
    telegram_id: int,
    position: int,
    word_card_ids: list[int],
) -> QuizQuestion | None:
    language = get_user_language(session, telegram_id)
    cards_by_id = {
        card.id: card
        for card in session.scalars(
            select(WordCard)
            .join(WordSet, WordSet.id == WordCard.word_set_id)
            .where(WordCard.id.in_(word_card_ids), WordSet.language == language)
        )
    }
    cards = [
        cards_by_id[word_card_id]
        for word_card_id in word_card_ids
        if word_card_id in cards_by_id
    ]
    if position < 1 or position > len(cards):
        return None

    current_card = cards[position - 1]
    question_random = random.Random(f"survival:{telegram_id}:{position}:{current_card.id}")
    all_translations = list(
        session.scalars(
            select(WordCard.translation)
            .join(WordSet, WordSet.id == WordCard.word_set_id)
            .where(
                WordSet.is_system.is_(True),
                WordSet.language == language,
                WordCard.id != current_card.id,
            )
        )
    )
    distractors = question_random.sample(all_translations, k=min(3, len(all_translations)))
    while len(distractors) < 3:
        distractors.append(f"Вариант {len(distractors) + 1}")

    options = distractors + [current_card.translation]
    question_random.shuffle(options)
    return QuizQuestion(
        set_code="survival",
        set_title="До первой ошибки",
        position=position,
        total=len(cards),
        word_card_id=current_card.id,
        foreign_word=current_card.foreign_word,
        correct_translation=current_card.translation,
        options=options,
    )


def build_dictionary_quiz_question(
    session: Session,
    telegram_id: int,
    position: int,
    word_card_ids: list[int],
) -> QuizQuestion | None:
    language = get_user_language(session, telegram_id)
    cards_by_id = {
        card.id: card
        for card in session.scalars(
            select(WordCard)
            .join(WordSet, WordSet.id == WordCard.word_set_id)
            .where(WordCard.id.in_(word_card_ids), WordSet.language == language)
        )
    }
    cards = [
        cards_by_id[word_card_id]
        for word_card_id in word_card_ids
        if word_card_id in cards_by_id
    ]
    if position < 1 or position > len(cards):
        return None

    current_card = cards[position - 1]
    question_random = random.Random(f"dictionary:{telegram_id}:{position}:{current_card.id}")
    all_translations = list(
        session.scalars(
            select(WordCard.translation)
            .join(WordSet, WordSet.id == WordCard.word_set_id)
            .where(
                WordSet.is_system.is_(True),
                WordSet.language == language,
                WordCard.id != current_card.id,
            )
        )
    )
    distractors = question_random.sample(all_translations, k=min(3, len(all_translations)))
    while len(distractors) < 3:
        distractors.append(f"Вариант {len(distractors) + 1}")

    options = distractors + [current_card.translation]
    question_random.shuffle(options)
    return QuizQuestion(
        set_code="dictionary",
        set_title="Мой словарь",
        position=position,
        total=len(cards),
        word_card_id=current_card.id,
        foreign_word=current_card.foreign_word,
        correct_translation=current_card.translation,
        options=options,
    )


def record_word_answer_progress(
    session: Session,
    telegram_id: int,
    word_card_id: int,
    is_correct: bool,
) -> bool:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False

    progress = session.scalar(
        select(UserWordProgress).where(
            UserWordProgress.user_id == user.id,
            UserWordProgress.word_card_id == word_card_id,
        )
    )
    if progress is None:
        progress = UserWordProgress(
            user_id=user.id,
            word_card_id=word_card_id,
            attempts=0,
            correct_answers=0,
            last_result=None,
        )
        session.add(progress)

    progress.attempts += 1
    if is_correct:
        progress.correct_answers += 1
    progress.last_result = is_correct
    session.flush()
    return True


def record_quiz_attempt(
    session: Session,
    telegram_id: int,
    set_code: str,
    total_questions: int,
    correct_answers: int,
) -> bool:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if set_code in SPECIAL_SET_CODES:
        set_code = build_special_word_set_code(get_user_language(session, telegram_id), set_code)
    word_set = session.scalar(select(WordSet).where(WordSet.code == set_code))
    if user is None:
        return False

    if word_set is not None:
        session.add(
            QuizAttempt(
                user_id=user.id,
                word_set_id=word_set.id,
                total_questions=total_questions,
                correct_answers=correct_answers,
            )
        )
    session.flush()
    return True


def get_progress_stats(session: Session, telegram_id: int) -> ProgressStats:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return ProgressStats(0, 0, 0, 0, 0)
    language = get_user_language(session, telegram_id)

    attempts_row = session.execute(
        select(
            func.count(QuizAttempt.id),
            func.coalesce(func.sum(QuizAttempt.total_questions), 0),
            func.coalesce(func.sum(QuizAttempt.correct_answers), 0),
            func.coalesce(func.max(QuizAttempt.correct_answers), 0),
        )
        .join(WordSet, WordSet.id == QuizAttempt.word_set_id)
        .where(QuizAttempt.user_id == user.id, WordSet.language == language)
    ).one()

    saved_words_count = session.scalar(
        select(func.count(UserWord.id))
        .join(WordCard, WordCard.id == UserWord.word_card_id)
        .join(WordSet, WordSet.id == WordCard.word_set_id)
        .where(UserWord.user_id == user.id, WordSet.language == language)
    ) or 0

    today = datetime.now().date()
    today_attempts = session.scalar(
        select(func.count(QuizAttempt.id)).where(
            QuizAttempt.user_id == user.id,
            func.date(QuizAttempt.created_at) == today,
        )
        .join(WordSet, WordSet.id == QuizAttempt.word_set_id)
        .where(WordSet.language == language)
    ) or 0

    weak_words_count = len(get_weak_word_cards(session, telegram_id, limit=1000))
    set_rows = session.execute(
        select(
            WordSet.title,
            func.coalesce(func.sum(QuizAttempt.correct_answers), 0),
            func.coalesce(func.sum(QuizAttempt.total_questions), 0),
        )
        .join(QuizAttempt, QuizAttempt.word_set_id == WordSet.id)
        .where(QuizAttempt.user_id == user.id, WordSet.language == language)
        .group_by(WordSet.id)
    ).all()
    set_scores = [
        (correct / total if total else 0, title)
        for title, correct, total in set_rows
        if total
    ]
    strongest_set_title = max(set_scores, default=(0, None), key=lambda item: item[0])[1]
    weakest_set_title = min(set_scores, default=(0, None), key=lambda item: item[0])[1]

    return ProgressStats(
        total_attempts=attempts_row[0],
        total_questions=attempts_row[1],
        total_correct=attempts_row[2],
        best_result=attempts_row[3],
        saved_words_count=saved_words_count,
        today_attempts=today_attempts,
        weak_words_count=weak_words_count,
        strongest_set_title=strongest_set_title,
        weakest_set_title=weakest_set_title,
    )
