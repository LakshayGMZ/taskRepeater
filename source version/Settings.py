import pickle
import os


class DataStorage:
    def __init__(self, filename="settings.pkl"):
        self.filename = filename
        self.data = self.load_data()

    def refresh(self):
        self.__init__(self.filename)

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as file:
                return pickle.load(file)
        else:
            return {}

    def _save_data(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)

    def create_record(self, key, value):
        self.data[key] = value
        self._save_data()
        self.refresh()
        print(f"Record with key '{key}' created.")

    def read_record(self, key):
        if key in self.data:
            return self.data[key]
        else:
            print(f"Record with key '{key}' not found.")
            return None

    def update_record(self, key, value):
        if key in self.data:
            self.data[key] = value
            self._save_data()
            self.refresh()
            print(f"Record with key '{key}' updated.")
        else:
            print(f"Record with key '{key}' not found.")

    def delete_record(self, key):
        if key in self.data:
            del self.data[key]
            self._save_data()
            print(f"Record with key '{key}' deleted.")
        else:
            print(f"Record with key '{key}' not found.")
