import re
import random
import webbrowser
import requests
from datetime import datetime
from textblob import TextBlob
import spacy
from spacy.cli import download

try:
    nlp = spacy.load("ru_core_news_sm")
except:
    try:
        download("ru_core_news_sm")
        nlp = spacy.load("ru_core_news_sm")
    except:
        nlp = None


class AdvancedChatBot:
    def __init__(self):
        self.context = {
            'user_name': None,
            'last_city': 'Москва',
            'known_entities': [],
            'weather_api_key': '3e4a1d7fbe47b282c514cacdd5f7f5fd',
            'current_topic': None  # Добавляем текущую тему разговора
        }

        self.chat_log = "chat_log.txt"

        self.positive_responses = [
            "Здорово!!!",
            "Рад за Вас.",
            "Это просто невероятно!!!",
            "Это замечательно!"
        ]

        self.feedback = [
            "Как у цифрового создания может быть? Нормально :)",
            "Лучше всех, спасибо что спросил! У тебя как?",
            "Дела у прокурора. А у меня делишки. Ты как?",
            "Всё пучком, а у тебя?"
        ]

        self.negative_responses = [
            "Да уж...дела...пупупу",
            "ЧЕ Ж ДЕЛАТЬ, ЧЕ Ж ДЕЛАТЬ...",
            "Отвратительно.",
            "Это грустно(",
            "Надеюсь, вскоре всё наладится. Хоть бы хоть бы..."
        ]

        self.greetings = [
            "Приветик",
            "Здравствуйте! Чем могу помочь?",
            "Ку"
        ]

        self.goodbyes = [
            "До свидания! Было приятно пообщаться.",
            "Пока! Возвращайтесь ещё!"
        ]

        self.whoyou = [
            "Я Бот",
            "Я бот, меня создала крутая, смешная, очень и очень красивая Зеленова Софья Алексеевна <3"
        ]

        self.topic_keywords = {
            'спорт': [
                r'\bфутбол[а-я]*\b', r'\bхоккей[а-я]*\b', r'\bбаскетбол[а-я]*\b', r'\bтеннис[а-я]*\b',
                r'\bспорт[а-я]*\b', r'\bматч[а-я]*\b', r'\bсоревновани[ея][а-я]*\b', r'\bчемпионат[а-я]*\b',
                r'\bолимпиад[а-я]*\b', r'\bтренировк[а-я]*\b', r'\bбег[а-я]*\b', r'\bплавани[а-я]*\b','мяч'
            ],
            'игры': [
                r'\bигр[ауы][а-я]*\b', r'\bгейм[а-я]*\b', r'\bконсол[а-я]*\b', r'\bsteam[а-я]*\b',
                r'\bplaystation[а-я]*\b', r'\bxbox[а-я]*\b', r'\bрпг[а-я]*\b', r'\bшутер[а-я]*\b',
                r'\bстратеги[а-я]*\b', r'\bквест[а-я]*\b', r'\bсимулятор[а-я]*\b', r'\bонлайн[а-я]*\b',
                r'\bмногопользовательск[а-я]*\b', r'\bодиночн[а-я]*\b', r'\bпрохожден[а-я]*\b',
                r'\bгеймпле[а-я]*\b', r'\bперсонаж[а-я]*\b', r'\bсюжет[а-я]*\b', r'\bграфик[а-я]*\b',
                r'\bмод[а-я]*\b', r'\bдостижен[а-я]*\b'
            ],
            'технологии': [
                r'\bкомпьютер[а-я]*\b', r'\bсмартфон[а-я]*\b', r'\bгаджет[а-я]*\b', r'\bпрограммир[а-я]*\b',
                r'\bискусственн[ый][а-я]*\b интеллект[а-я]*\b', r'\bробот[а-я]*\b', r'\bтехнологи[а-я]*\b',
                r'\bинноваци\b', r'\bайти\b', r'\bсоцсет\b', r'\bинтернет\b',
                r'\bданн[а-я]*\b', r'\bкибер[а-я]*\b', r'\bвиртуальн[а-я]*\b реальность[а-я]*\b'
            ]
        }

        self.topic_responses = {
            'спорт': [
                "О, вы интересуетесь спортом? Это прекрасно!",
                "Спорт - это здорово! Какой вид спорта вам нравится?",
                "Я тоже люблю следить за спортивными событиями!"
            ],
            'игры': [
                "О, игры! Это моя любимая тема! Во что играете?",
                "Компьютерные игры - это целый мир! Какие жанры вам нравятся?",
                "Я обожаю игры! На какой платформе вы играете?",
                "Какую последнюю игру вы прошли? Хотите обсудить?",
                "Игры - это интересно! Какая игра произвела на вас самое большое впечатление?"
            ],
            'технологии': [
                "Технологии - это мой конёк! Что вас интересует?",
                "О, технологии! Это же будущее! Какая область вам наиболее интересна?",
                "Я сам продукт современных технологий! Хотите обсудить что-то конкретное?"
            ]
        }

        with open(self.chat_log, 'w', encoding='utf-8') as f:
            f.write("______Начало чата______\n")

    def save_to_log(self, user_message, bot_response):
        with open(self.chat_log, 'a', encoding='utf-8') as f:
            f.write(f"Пользователь: {user_message}\n")
            f.write(f"Бот: {bot_response}\n\n")

    def analyze_sentiment(self, text):
        text_lower = text.lower()
        pos_words = [
            r'\bхорош[а-я]*\b', r'\bотличн[а-я]*\b', r'\bпрекрасн[а-я]*\b',
            r'\bрад[а-я]*\b', r'\bсчастлив[а-я]*\b', 'ура',
            r'\bвесел[а-я]*\b', r'\bчетк[юя][а-я]*\b',
            r'\bневероятн[юя][а-я]*\b', 'гуд'
        ]
        neg_words = [
            r'\bплох[а-я]*\b', r'\bужасн[а-я]*\b', r'\bгрустн[а-я]*\b',
            r'\bзл[а-я]*\b', r'\bраздраж[а-я]*\b', r'\bустал[а-я]*\b',
            r'\bотвратительн[а-я]*\b', r'\bустал[а-я]*\b', 'все тлен', 'бе'
        ]

        pos = sum(1 for word in pos_words if re.search(word, text_lower))
        neg = sum(1 for word in neg_words if re.search(word, text_lower))

        if pos > neg: return "positive"
        if neg > pos: return "negative"
        return "neutral"

    def detect_topic(self, text):
        text_lower = text.lower()
        topic_scores = {topic: 0 for topic in self.topic_keywords}

        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text_lower):
                    topic_scores[topic] += 1

        # Находим тему с максимальным количеством совпадений
        max_topic = max(topic_scores, key=topic_scores.get)

        # Если есть хоть одно совпадение с ключевыми словами
        if topic_scores[max_topic] > 0:
            self.context['current_topic'] = max_topic
            return max_topic
        return None

    def extract_entities(self, text):
        if not nlp:
            return {'PER': [], 'LOC': [], 'ORG': [], 'MISC': []}

        doc = nlp(text)
        entities = {'PER': [], 'LOC': [], 'ORG': [], 'MISC': []}

        for ent in doc.ents:
            if ent.label_ == "PER":
                entities['PER'].append(ent.text)
            elif ent.label_ == "LOC":
                entities['LOC'].append(ent.text)
                self.context['last_city'] = ent.text
            elif ent.label_ == "ORG":
                entities['ORG'].append(ent.text)
            else:
                entities['MISC'].append(ent.text)

        return entities

    def get_current_time(self):
        return datetime.now().strftime("%H:%M")

    def get_current_date(self):
        return datetime.now().strftime("%d.%m.%Y")

    def get_weather(self, city=None):
        city = city or self.context['last_city']
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.context['weather_api_key']}&units=metric&lang=ru"
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                weather = {
                    'city': data['name'],
                    'temp': data['main']['temp'],
                    'desc': data['weather'][0]['description'],
                    'feels_like': data['main']['feels_like']
                }
                return f"Погода в {weather['city']}: {weather['desc']}, {weather['temp']}°C (ощущается как {weather['feels_like']}°C)"
            return "Не могу получить данные о погоде"
        except:
            return "Ошибка запроса погоды"

    def search_internet(self, query):
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Ищу информацию о {query}"

    def process_message(self, message):
        message = message.strip()
        if not message:
            return "Вы ничего не написали..."

        lower_msg = message.lower()
        entities = self.extract_entities(message)

        # 1. Сначала проверяем имя
        if entities['PER'] and not self.context['user_name']:
            self.context['user_name'] = entities['PER'][0]
            response = random.choice([
                f"Приятно познакомиться, {self.context['user_name']}!",
                f"Красивое имя, {self.context['user_name']}!"
            ])
            self.save_to_log(message, response)
            return response

        # 2. Определяем тему разговора
        detected_topic = self.detect_topic(message)
        if detected_topic:
            if self.context['current_topic'] != detected_topic:
                self.context['current_topic'] = detected_topic
                response = random.choice(self.topic_responses[detected_topic])
                self.save_to_log(message, response)
                return response
            else:

                 if detected_topic == 'спорт':
                     response = random.choice([
                         "Какой ваш любимый спортивный клуб?",
                         "Следите ли вы за какими-то конкретными соревнованиями?",
                         "Спорт - это здоровый образ жизни!"
                     ])
                 elif detected_topic == 'игры':
                     response = random.choice([
                         "Что вы думаете о последних релизах?",
                         "Игровое комьюнити очень интересное. не так ли?",
                         "Как вы считаете, какие жанры самые популярные?"
                     ])
                 elif detected_topic == 'технологии':
                     response = random.choice([
                         "Какие технологии вас больше всего впечатляют?",
                         "Как вы относитесь к искусственному интеллекту?",
                         "Какое техническое устройство вы считаете самым полезным?"
                     ])
            self.save_to_log(message, response)
            return response

        # 3. Затем анализируем тональность
        sentiment = self.analyze_sentiment(lower_msg)
        if sentiment == "positive":
            response = random.choice(self.positive_responses)
            self.save_to_log(message, response)
            return response
        elif sentiment == "negative":
            response = random.choice(self.negative_responses)
            self.save_to_log(message, response)
            return response

        # 4. Проверяем специальные вопросы
        if re.search(r'(как меня зовут|мое имя)', lower_msg):
            if self.context['user_name']:
                response = f"Вы сказали, что вас зовут {self.context['user_name']}!"
            else:
                response = "Я пока не знаю вашего имени. Как вас зовут?"
            self.save_to_log(message, response)
            return response

        # 5. Обрабатываем команды
        if re.search(r'(привет|ку|хай|приветствую|здравствуйте|здравствуй|приветик)', lower_msg):
            response = random.choice(self.greetings)
            self.save_to_log(message, response)
            return response

        if re.search(r'(пока|до свидания|выход)', lower_msg):
            response = random.choice(self.goodbyes)
            self.save_to_log(message, response)
            return response

        if re.search(r'(как дела\??)', lower_msg):
            response = random.choice(self.feedback)
            self.save_to_log(message, response)
            return response

        if re.search(r'(как тебя зовут\??|кто ты\??|ты человек\??|ты робот\??)', lower_msg):
            response = random.choice(self.whoyou)
            self.save_to_log(message, response)
            return response

        if re.search(r'(сколько времени|время|текущее время|время сейчас)', lower_msg):
            response = f"Котлы показывают {self.get_current_time()}"
            self.save_to_log(message, response)
            return response

        if re.search(r'(какое число|дата|текущая дата)', lower_msg):
            response = f"Сегодня {self.get_current_date()}"
            self.save_to_log(message, response)
            return response

        if re.search(r'(погода)', lower_msg):
            city = entities['LOC'][0] if entities['LOC'] else None
            response = self.get_weather(city)
            self.save_to_log(message, response)
            return response

        if re.search(r'(найди|поиск|ищи)', lower_msg):
            query = re.sub(r'(найди|поиск|ищи)', '', message, flags=re.IGNORECASE).strip()
            if query:
                response = self.search_internet(query)
            else:
                response = "Что именно нужно найти?"
            self.save_to_log(message, response)
            return response

        # 6. Ответ по умолчанию
        response = random.choice([
            "Понял принял. Что ещё расскажете?",
            "Интересненько.",
            "Ясно."
        ])
        self.save_to_log(message, response)
        return response


def main():
    bot = AdvancedChatBot()
    print("Бот запущен. Напишите 'пока' для выхода.")

    while True:
        user_input = input("Вы: ")
        response = bot.process_message(user_input)
        print("Бот:", response)

        if user_input.lower() in ['пока', 'выход']:
            break


if __name__ == "__main__":
    main()