class Card:
    def __init__(self, owner_name) -> None:
        self.owner_name = owner_name

    @property
    def num(self):
        return '4242424242424242'

    @property
    def date(self):
        return '02/23'

    @property
    def cvc(self):
        return '123'