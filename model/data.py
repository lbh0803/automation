from collections import defaultdict
import logging
from functools import lru_cache


class DataModel:
    """
    This is class for dictionary, it can handle key error
    and support nested dictionary structure.
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

    # @lru_cache(maxsize=10)
    # Cache is inefficient because of various inputs and low repetitive access.
    def get_data(self, key_path):
        """
        This can support recursive dict.
        You can use like below, (seperator should be .)
        instance.get_data(user.home.room.bed)
        """
        keys = key_path.split(".")
        current_dict = self.data
        for idx in range(len(keys) - 1):
            try:
                current_dict = current_dict[keys[idx]]
            except KeyError:
                logging.error(f"The {idx}th key {keys[idx]} is not in {self._name}")
                raise
        return current_dict[keys[-1]]

    def set_data(self, key_path, value):
        """
        This can support recursive dict.
        You can use like below, (seperator should be .)
        instance.set_data(user.home.bed) = simons
        """
        keys = key_path.split(".")
        current_dict = self.data
        for idx in range(len(keys) - 1):
            if keys[idx] not in current_dict:
                current_dict[keys[idx]] = dict()
            current_dict = current_dict[keys[idx]]
        current_dict[keys[-1]] = value

    def show_all(self, dictionary=None, indent=0):
        """
        This can show all key:value
        and support indented view.
        """
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

    def __init__(self):
        self._query = dict()
        self._cnt = 0
        self._repeat = defaultdict(bool)
        self._repeat_cnt = defaultdict(int)
        self._repeat_break = False

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    def get_query(self):
        """
        Can return sub dict according to self._cnt.
        """
        result = self.query.get(self._cnt, None)
        if not result:
            raise Exception(f"No dictionary for cnt {self._cnt} has been assigned")
        return result

    def set_query(self, repeat, cnt, var, BaseInputWidget, *args):
        obj = BaseInputWidget(*args)
        if not self.query.get(cnt):
            self.query[cnt] = dict()
        self.query[cnt][var] = obj
        self._repeat[cnt] = repeat
        self._repeat_cnt[cnt] = 1

    def up_cnt(self):
        """
        Next button is blocked when it is last window
        """
        if not self.is_repeat_type() or self._repeat_break:
            self._cnt += 1
        else:
            self._repeat_cnt[self._cnt] += 1

    def down_cnt(self):
        """
        Back button doesn't exist when it is first window
        """
        if self._repeat_cnt[self._cnt] > 1:
            self._repeat_cnt[self._cnt] -= 1
        else:
            self._cnt -= 1

    def is_repeat_type(self):
        """
        If the number of input window is not fixed,
        You should use repeat type.
        ex) Get test mode information sequentially
        """
        return self._repeat[self._cnt]

    def set_repeat_break(self, value):
        self._repeat_break = value
        logging.info(f"Repeat break is called break : {self._repeat_break}, go to next step")

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
