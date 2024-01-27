class DataDict:
    """
    This is class for dictionary, it can handle key error
    And support nested dictionary structure.
    """

    def __init__(self, name=None):
        self._data = dict()
        self._name = name

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    # def get_data(self, key, default=None):
    #     result = self.data.get(key, default)
    #     if result == default:
    #         raise Exception(f"The key {key} is not in dict {self._name}")
    #     return result

    # def set_data(self, key, value):
    #     self.data[key] = value

    def get_data(self, key_path):
        keys = key_path.split(".")
        current_dict = self.data
        for idx in range(len(keys) - 1):
            try:
                current_dict = current_dict[keys[idx]]
            except KeyError:
                print(f"The {idx}th key {keys[idx]} is not in {self._name}")
                raise
        return current_dict[keys[-1]]

    def set_data(self, key_path, value):
        keys = key_path.split(".")
        current_dict = self.data
        for idx in range(len(keys) - 1):
            if keys[idx] not in current_dict:
                current_dict[keys[idx]] = dict()
            current_dict = current_dict[keys[idx]]
        current_dict[keys[-1]] = value

    def show_all(self, dictionary=None, indent=0):
        if not dictionary:
            dictionary = self.data
        for key, value in dictionary.items():
            if isinstance(value, dict):
                print("     " * indent + f"key : {key}, value: sub_dict")
                self.show_all(value, indent + 1)
            else:
                print("     " * indent + f"key : {key}, value: {value}")


class Query:
    """
    This is special class for input query.
    """

    def __init__(self, repeat=None):
        self._query = dict()
        self._cnt = 0
        self._repeat = repeat
        self._repeat_cnt = 1

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    def get_query(self):
        result = self.query.get(self._cnt, None)
        if not result:
            raise Exception(f"No dictionary for cnt {self._cnt} has been assigned")
        return result

    def set_query(self, key, var, BaseInputWidget, *args):
        obj = BaseInputWidget(*args)
        if not self.query.get(key):
            self.query[key] = dict()
        self.query[key][var] = obj

    def up_cnt(self):
        if not self.is_last():
            self._cnt += 1
        else:
            self._repeat_cnt += 1

    def down_cnt(self):
        if self._repeat_cnt > 1:
            self._repeat_cnt -= 1
        elif not self.is_first():
            self._cnt -= 1

    def is_repeat_type(self):
        return self._repeat

    def is_last(self):
        if self._cnt == len(self.query) - 1:
            return True
        else:
            return False

    def is_first(self):
        if self._cnt == 0:
            return True
        else:
            return False
