class User:
    def  __init__(self, id, name, last_name, address, city, state, phone_num, email, password) -> None:
        self.id = id
        self.name = name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.phone_num = phone_num
        self.email = email
        self.password = password

    def __repr__(self) -> str:
        rep = 'User name: ' + str(self.name) + ' last name: ' + str(self.last_name) + ' email: ' + str(self.email)
        return rep