PROMPT = {
    "hello": "<Name>, добрый день! Вас беспокоит компания X, мы проводим опрос удовлетворенности нашими услугами. Подскажите, вам удобно сейчас говорить?",
    "hello_repeat": "Это компания X. Подскажите, вам удобно сейчас говорить?",
    "hello_null": "Извините, вас не слышно. Вы могли бы повторить?",
    "recommend_main": "Скажите, а готовы ли вы рекомендовать нашу компанию своим друзьям? Оцените, пожалуйста, по шкале от «0» до «10», где «0» - не буду рекомендовать, «10» - обязательно порекомендую.",
    "recommend_repeat": "Как бы вы оценили возможность порекомендовать нашу компанию своим знакомым по шкале от 0 до 10, где 0 - точно не порекомендую, 10 - обязательно порекомендую.",
    "recommend_repeat_2": "Ну если бы вас попросили порекомендовать нашу компанию друзьям или знакомым, вы бы стали это делать? Если «да» - то оценка «10», если точно нет – «0».",
    "recommend_score_negative": "Ну а от 0 до 10 как бы вы оценили бы: 0, 5 или может 7?",
    "recommend_score_neutral": "Ну а от 0 до 10 как бы вы оценили?",
    "recommend_score_positive": "Хорошо,  а по 10-ти бальной шкале как бы вы оценили 8-9 или может 10?",
    "recommend_null": "Извините вас свосем не слышно,  повторите пожалуйста?",
    "recommend_default": "повторите пожалуйста ",
    "hangup_positive": "Отлично!  Большое спасибо за уделенное время! Всего вам доброго!",
    "hangup_negative": "Я вас понял. В любом случае большое спасибо за уделенное время! Всего вам доброго.",
    "hangup_wrong_time": "Извините пожалуйста за беспокойство. Всего вам доброго.",
    "hangup_null": "Вас все равно не слышно, будет лучше если я перезвоню. Всего вам доброго",
    "forward": "Чтобы разобраться в вашем вопросе, я переключу звонок на моих коллег. Пожалуйста, оставайтесь на линии."
}

SCORE = {
    'ноль': 0, 'один': 1, 'два': 2, 'три': 3, 'четыре': 4,
    'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10
}

TELEPHONE_NUMBER = '89876543210'
CALL_DATE = '01-10-2022 12:00:00'
HELLO_ENTITIES = ['да', 'нет', 'занят', 'еще раз']
RECOMMEND_ENTITIES = [
    'да', 'нет', 'занят', 'еще раз', 'возможно', 'не знаю', 'вопрос', 'ноль', 'один', 'два', 'три', 'четыре', 'пять',
    'шесть', 'семь', 'восемь', 'девять', 'десять'
]

class HelloLogic:
    """Класс для группировки скриптов приветственной части звонка."""

    @classmethod
    def get_answer(cls):
        with nv.listen(entities=HELLO_ENTITIES) as r:
            pass
        result = nlu.extract()
        return result

    @classmethod
    def parse_response(cls, result):
        if not result.has_entities():
            cls.hello_null()
        elif result.has_entity('да'):
            nn.env('confirm', val=True)
            MainLogic.recommend_main()
        elif result.has_entity('нет'):
            nn.env('confirm', val=False)
            HangupLogic.hangup_wrong_time()
        elif result.has_entity('занят'):
            nn.env('wrong_time', val=True)
            HangupLogic.hangup_wrong_time()
        elif result.has_entity('еще раз'):
            nn.env('repeat', val=True)
            cls.hello_repeat()
        else:
            MainLogic.recommend_main()

    @classmethod
    def hello(cls):
        with nv.listen() as r:
            nv.say(PROMPT["hello"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def hello_repeat(cls):
        with nv.listen() as r:
            nv.say(PROMPT["hello_repeat"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def hello_null(cls):
        with nv.listen() as r:
            nv.say(PROMPT["hello_null"])
        result = cls.get_answer()
        if not result.has_entities():
            HangupLogic.hangup_null()
        else:
            cls.parse_response(result)


class MainLogic:
    """Класс для группировки скриптов основной части звонка."""

    @classmethod
    def get_answer(cls):
        with nv.listen(entities=RECOMMEND_ENTITIES) as r:
            pass
        result = nlu.extract()
        return result

    @classmethod
    def parse_response(cls, result):
        for i in SCORE.keys():
            if result.has_entity(i):
                nn.env('recommendation_score', val=SCORE[i])
                HangupLogic.hangup_negative() if SCORE[i] < 9 else HangupLogic.hangup_positive()
        if not result.has_entities():
            cls.recommend_null()
        elif result.has_entity('нет'):
            nn.env('recommendation', val='negative')
            cls.recommend_score_negative()
        elif result.has_entity('да'):
            nn.env('recommendation', val='positive')
            cls.recommend_score_positive()
        elif result.has_entity('возможно'):
            nn.env('recommendation', val='neutral')
            cls.recommend_score_neutral()
        elif result.has_entity('еще раз'):
            nn.env('repeat', val=True)
            cls.recommend_repeat()
        elif result.has_entity('не знаю'):
            nn.env('recommendation', val='dont_know')
            cls.recommend_repeat_2()
        elif result.has_entity('занят'):
            nn.env('wrong_time', val=True)
            HangupLogic.hangup_wrong_time()
        elif result.has_entity('вопрос'):
            nn.env('question', val=True)
            ForwardLogic.forward()
        else:
            cls.recommend_default()

    @classmethod
    def recommend_main(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_main"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def recommend_repeat(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_repeat"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def recommend_repeat_2(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_repeat_2"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def recommend_score_negative(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_score_negative"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def recommend_score_neutral(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_score_neutral"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def recommend_score_positive(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_score_positive"])
        result = cls.get_answer()
        cls.parse_response(result)

    @classmethod
    def recommend_null(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_null"])
        result = cls.get_answer()
        if not result.has_entities():
            HangupLogic.hangup_null()
        else:
            cls.parse_response(result)

    @classmethod
    def recommend_default(cls):
        with nv.listen() as r:
            nv.say(PROMPT["recommend_default"])
        result = cls.get_answer()
        for entity in RECOMMEND_ENTITIES:
            if result.has_entity(entity):
                cls.parse_response(result)
        HangupLogic.hangup_null()


class HangupLogic:
    """Класс для группировки скриптов завершающей части звонка."""

    @classmethod
    def hangup_positive(cls):
        with nv.listen() as r:
            nv.say(PROMPT["hangup_positive"])
        nn.dialog.result = nn.RESULT_DONE

    @classmethod
    def hangup_negative(cls):
        with nv.listen() as r:
            nv.say(PROMPT["hangup_negative"])
        nn.dialog.result = nn.RESULT_DONE

    @classmethod
    def hangup_wrong_time(cls):
        with nv.listen() as r:
            nv.say(PROMPT["hangup_wrong_time"])
        nn.dialog.result = nn.RESULT_DONE

    @classmethod
    def hangup_null(cls):
        with nv.listen() as r:
            nv.say(PROMPT["hangup_null"])
        nn.dialog.result = nn.RESULT_DONE


class ForwardLogic:
    """Класс для группировки скриптов перевода звонка."""

    @classmethod
    def forward(cls):
        with nv.listen() as r:
            nv.say(PROMPT["forward"])
        bridge_action()


def bridge_action():
    """Метод для перевода звонка на оператора."""
    pass


if __name__ == "__main__":
    nn.call(msisdn=TELEPHONE_NUMBER, date=CALL_DATE, entry_point=HelloLogic.hello())
