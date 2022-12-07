class Transaction:
    def __init__(self, id, sender, receiver, amount, date, currency, state) -> None:
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.date = date
        self.currency = currency
        self.state = state

    def __repr__(self) -> str:
        rep = 'Transaction (' + str(self.id) + ', ' + self.sender + ' -> ' + self.receiver + ' [ ' + str(self.amount) + ' ' + self.currency + ' ] )'
        return rep