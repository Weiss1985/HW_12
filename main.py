import pickle
from datetime import datetime

class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __str__(self):
        return str(self._value)

class Name(Field):
    pass

class Phone(Field):
    @Field.value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self._value = value
        else:
            raise ValueError('Помилка, номер повинен складатися з 10 цифр.')

class Birthday(Field):
    def is_valid(self, value):
        super().__init(value)
        try:
            datetime.strptime(value, '%d-%m-%Y')
        except ValueError:
            print('Недійсний формат дня народження. Спробуйте ДД-ММ-РРРР.')

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        phone = Phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone):
        for phone in self.phones:
            if phone.value == phone:
                self.phones.remove(phone)
                return self.phones
        raise ValueError('Невірний номер.')

    def edit_phone(self, old_phone, edit_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = edit_phone
                return phone.value
        raise ValueError('Невірний номер.')

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Контактна Особа: {self.name.value}, телефон: {'; '.join(p.value for p in self.phones)}."

    def days_to_birthday(self):
        if not self.birthday:
            return None

        today = datetime.now()
        birthday_date = datetime(self.birthday.value.day, self.birthday.value.month, self.birthday.value.year)

        if today > birthday_date:
            next_birthday = datetime(self.birthday.value.day, self.birthday.value.month, self.birthday.value.year + 1)
        else:
            next_birthday = birthday_date

        days_left = (next_birthday - today).days
        return days_left

class AddressBook:
    FILENAME = "address_book.pi"

    def __init__(self):
        self.load_from_file()

    def add_record(self, record):
        if record.name.value in self.data:
            choice = input("Контакт з таким ім'ям вже існує. Бажаєте оновити існуючий запис? (так/ні): ")
            if choice.lower() == "так":
                self.edit_record(record.name.value, record.phones[0].value)
                print(f"Контакт оновлено: {record.name.value} - {record.phones[0].value}")
            elif choice.lower() == "ні":
                print("Дія відмінена. Немає змін у контактах.")
            else:
                print("Невірна відповідь. Дія відмінена.")
        else:
            self.data[record.name.value] = record
            self.save_to_file()

    def edit_record(self, name, new_phone):
        if name in self.data:
            record = self.data[name]
            record.edit_phone(record.phones[0].value, new_phone)
            self.save_to_file()
        else:
            print("Контакт не знайдений.")

    def find(self, name):
        if name in self.data:
            return self.data[name]

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            self.save_to_file()

    def save_to_file(self):
        with open(self.FILENAME, 'wb') as file:
            pickle.dump(self.data, file)
        print(f"Адресну книгу збережено у файл {self.FILENAME}")

    def load_from_file(self):
        try:
            with open(self.FILENAME, 'rb') as file:
                self.data = pickle.load(file)
                print(f"Адресну книгу завантажено із файлу {self.FILENAME}")
        except FileNotFoundError:
            self.data = {}

    def search(self, query):
        results = []
        for record in self.data.values():
            if query in record.name.value:
                results.append(record)
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
        return results

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError):
            return "Невірний ввід. Будь ласка, спробуйте ще раз."
    return wrapper

@input_error
def main():
    address_book = AddressBook()

    def parse_command(command):
        command_parts = command.strip().split(' ', 1)
        if len(command_parts) < 1:
            return None, None
        command_type = command_parts[0].lower()
        args = command_parts[1] if len(command_parts) > 1 else None
        return command_type, args

    def handle_add(args):
        if args:
            name, phone = args.split(' ', 1)
            record = Record(name)
            record.add_phone(phone)
            address_book.add_record(record)
            return f"Контакт успішно доданий: {name} - {phone}"
        else:
            return "Будь ласка, введіть ім'я та номер телефону."

    def handle_edit(args):
        if args:
            name, phone = args.split(' ', 1)
            address_book.edit_record(name, phone)
            return f"Контакт оновлено: {name} - {phone}"
        else:
            return "Будь ласка, введіть ім'я та новий номер телефону."

    def handle_show_all():
        result = "Контакти:\n"
        for record in address_book.data.values():
            result += f"{record.name.value} - {', '.join(p.value for p in record.phones)}\n"
        return result.strip()

    def handle_find(args):
        if args:
            results = address_book.search(args)
            if results:
                result_str = "Результати пошуку:\n"
                for record in results:
                    result_str += f"{record.name.value} - {', '.join(p.value for p in record.phones)}\n"
                return result_str.strip()
            else:
                return "Не знайдено відповідних контактів."
        else:
            return "Будь ласка, введіть пошуковий запит."

    while True:
        command = input("Введіть команду: ")
        command_type, args = parse_command(command)
        
        if command_type in ["додати", "add"]:
            print(handle_add(args))
        elif command_type in ["редагувати", "edit"]:
            print(handle_edit(args))
        elif command_type in ["показати", "show"]:
            print(handle_show_all())
        elif command_type in [ "пошук", "search"]:
            print(handle_find(args))
        elif command_type in ["видалити", "delete"]:
            address_book.delete(args)
            print(f"Контакт {args} видалено.")
        elif command_type in ["вихід", "завершити", "quit", "exit"]:
            break
        else:
            print("Невідома команда. Будь ласка, спробуйте ще раз.")

if __name__ == "__main__":
    main()
