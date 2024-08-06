class FAQ:
    count_id = 0

    def __init__(self, question, answer):
        FAQ.count_id += 1
        self.__faq_id = FAQ.count_id
        self.__question = question
        self.__answer = answer

    def get_faq_id(self):
        return self.__faq_id

    def get_question(self):
        return self.__question

    def get_answer(self):
        return self.__answer

    def set_question(self, question):
        self.__question = question

    def set_answer(self, answer):
        self.__answer = answer
