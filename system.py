import os
from pandas import DataFrame
import mail_system


def create_dir(path: str):
    if not os.path.isdir(path):
        os.makedirs(path)


def sort_dict_by_recency(dictionary: dict):
    recency_list = []

    for key in dictionary:
        recency_list.append((dictionary[key]['recency'], key))
    recency_list = sorted(recency_list, key=lambda tup: tup[0], reverse=True)
    return_dict = {}

    for key in [element[1] for element in recency_list]:
        return_dict[key] = dictionary[key]
    return return_dict


def sort_dict(dictionary: dict):
    key_list = list(dictionary.keys())
    return_dict = {}
    for element in sorted(key_list):
        return_dict[element] = dictionary[element]
    return return_dict


def create_file(path: str, content: str):
    if not os.path.isfile(path):
        open(path, 'w+').write(content)


def rnd(number):
    return round(number, 2)


class System:
    def __init__(self):
        """
        initializes the System class
        """

        # setup directories

        if not os.path.isdir('data'):
            os.makedirs('data')

        create_file('data/users.txt', "{'Freddie': {'items': {0: 7, 1: 3}, 'credit': 20}, "
                                      "'Lisa Schneider': {'items': {0: 1, 1: 13}, "
                                      "'credit': 0}}")
        create_file('data/items.txt',
                    "{'Brauhause Allgemeines': {'price': 0.8, 'crate_size': 24}, "
                    "'CokePopTM': {'price': 1.25, 'crate_size': 6}}")
        create_file('data/settings.txt', "{'notification-mail': 'your-mail@yourmail.com', 'notification-threshold': 1}")

        # load contents:
        self.users = sort_dict_by_recency(eval(open('data/users.txt').read().replace('\n', ''))) if open('data/users.txt').read().replace(
            '\n', '') != '' else {}
        self.items = eval(open('data/items.txt').read().replace('\n', '')) if open('data/items.txt').read().replace(
            '\n', '') != '' else {}

        # load settings:
        self.settings = eval(open('data/settings.txt').read().replace('\n', ''))

        # setup mail_system:
        self.mail_system = mail_system.Mail_System()

    def update(self):
        self.users = sort_dict_by_recency(self.users)
        self._update_users_()
        self.items = sort_dict(self.items)
        self._update_items_()

    def consume_item(self, user_id: str, item_id: str, amount: int):
        self._update_recency_(user_id)
        if self.items[item_id]['in_stock'] >= amount:
            if self.users[user_id]['items'].get(item_id) is None:
                self.users[user_id]['items'][item_id] = 0
            self.users[user_id]['items'][item_id] += amount
            self.users[user_id]['credit'] -= amount * self.items[item_id]['price']
            self.users[user_id]['credit'] = rnd(self.users[user_id]['credit'])
            self.items[item_id]['in_stock'] -= amount

            returner = f'{amount} of {item_id} for {user_id} was added. total is now {self.users[user_id]["items"][item_id]}. '
        else:
            returner = f'Storage insufficient. [{self.items[item_id]["in_stock"]}/{amount}]'
        self.update()
        if self.items[item_id]['in_stock'] <= self.items.get(item_id).get('crate_size') * self.settings[
            'notification-threshold']:
            message = f'Subject: {item_id} is running low.\n\nThere are about {self.items[item_id]["in_stock"]} bottles remaining.'
            self.mail_system.send_mail(self.settings['notification-mail'], message)
        print(returner)
        return returner

    def invoice(self):
        message_str = 'Subject: Invoice Item System\n\nName:\tCredit:\n'
        for user in sort_dict(self.users):
            message_str += f'{user}\t{self.users[user]["credit"]}\n'
        self.mail_system.send_mail(self.settings['notification-mail'], message_str)

    def add_user(self, display_name: str):
        if display_name not in [element['display_name'] for element in self.users.values()]:
            self.users[display_name] = {'items': {}, 'display_name': display_name, 'credit': 0, 'recency': 0}
            print(f'{display_name} successfully added')
        else:
            print(f'{display_name} seems to already be a user')
        self._update_recency_(display_name)
        self.update()

    def add_item(self, display_name: str, price: int, crate_size: int):
        dictionary = {'display_name': display_name, 'price': price, 'crate_size': crate_size, 'in_stock': 0}
        if dictionary not in self.items.values():
            self.items[display_name] = dictionary
            print(f'{display_name} successfully added')
        else:
            print(f'{display_name} seems to already be an item')
        self.update()

    def recount_stocked_items(self, item_id: str, amount: int):
        self.items[item_id]['in_stock'] = amount
        self.update()

    def restock(self, item_id: str, amount: int, is_crate: bool):
        if is_crate:
            total = amount * self.items[item_id]['crate_size']
        else:
            total = amount
        self.items[item_id]['in_stock'] += total
        message = f'Subject: {item_id} has been restocked.\n\nThere should be about {self.items[item_id]["in_stock"]} left.'
        self.mail_system.send_mail(self.settings['notification-mail'], message)
        self.update()

    def credit(self, user_id: str, amount: int):
        if self.users.get(user_id) is not None:
            self.users[user_id]['credit'] += amount
        self.update()

    def print_items(self):
        names = []
        prices = []
        crate_sizes = []

        for item in self.items.values():
            names.append(item['display_name'])
            prices.append(item['price'])
            crate_sizes.append(item['crate_size'])

        print_dataframe = DataFrame(data={'Names: ': names, 'Prices: ': prices, 'Crate Size: ': crate_sizes})
        print(print_dataframe)

    def print_users(self):
        data = {}
        data['Names:'] = []
        data['Credit:'] = []
        for user in self.users.values():
            data['Names:'].append(user['display_name'])
            data['Credit:'].append(user['credit'])
        for item in self.items:
            data[f"{self.items[item]['display_name']}:"] = []
            for user in self.users.values():
                data[f"{self.items[item]['display_name']}:"].append(
                    user['items'].get(item) if user['items'].get(item) is not None else 0)

        print_dataframe = DataFrame(data=data)
        print(print_dataframe)

    def get_table(self):
        data = {}
        data['Namen'] = []
        data['Guthaben'] = []
        for user in self.users:
            data['Namen'].append(user)
            data['Guthaben'].append(self.users[user]['credit'])
        for item in self.items:
            data[f"{item}:"] = []
            for user in self.users.values():
                data[f"{item}:"].append(
                    user['items'].get(item) if user['items'].get(item) is not None else 0)

        return DataFrame(data=data)

    def return_stocked_items(self):
        return_list = []
        for item in self.items:
            if self.items[item]['in_stock'] >= 1:
                return_list.append(item)
        return return_list

    def print_stocked_items(self):
        data = {}
        data['Names:'] = self.items.keys()
        data['In Stock:'] = [item['in_stock'] for item in self.items]

    def reset_user_stats(self):
        for user in self.users:
            for item in self.users[user]['items']:
                self.users[user]['items'][item] = 0
        self.update()

    def _update_recency_(self, user_id):
        self.users[user_id]['recency'] = len(self.users) - 1
        for user in self.users:
            if self.users[user]['recency'] >= 1:
                self.users[user]['recency'] -= 1
        self.update()

    def _update_users_(self):
        open('data/users.txt', 'w').write(str(sort_dict_by_recency(self.users)))

    def _update_items_(self):
        open('data/items.txt', 'w').write(str(sort_dict(self.items)))
