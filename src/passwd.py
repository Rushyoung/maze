import hashlib
import json


def encrypt(string: str) -> str:
    salt = b'\xb2S"e}\xdf\xb0\xfe\x9c\xde\xde\xfe\xf3\x1d\xdc>'
    string_bytes = string.encode('utf-8')
    hash_obj = hashlib.sha256(salt + string_bytes)
    return hash_obj.hexdigest()


def verify(string: str, hash_value: str) -> bool:
    return encrypt(string) == hash_value


class tip:
    def __init__(self, alist: list[int]):
        assert len(alist) == 3 or len(alist) == 2, "List must contain 2 or 3 elements"
        self.alist = alist
        self.strategy = None
        if len(alist) == 3 and alist.count(-1) == 2:
                self.strategy = "place"
        elif len(alist) == 2:
            if alist[1] == 1:
                self.strategy = "odd"
            elif alist[1] == 0:
                self.strategy = "even"
            elif all(x == -1 for x in alist):
                self.strategy = "prime"
        assert self.strategy is not None, "Invalid tip strategy"

    def msg(self):
        if self.strategy == "prime":
            return "每位密码为素数且不重复"
        if self.strategy == "odd":
            return f"第{self.alist[0]}位密码为奇数"
        if self.strategy == "even":
            return f"第{self.alist[0]}位密码为偶数"
        if self.strategy == "place":
            place = -1
            for i in range(3):
                if self.alist[i] != -1:
                    place = i + 1
                    break
            else:
                raise ValueError("Invalid place strategy")
            return f"第{place}位是数字{self.alist[place - 1]}"
        
    def data(self):
        return self.alist


class cracker:
    def __init__(self, file: str):
        self.file = file
        with open(file, 'r') as f:
            self.data = json.load(f)
        self.hash = self.data['L']
        self.cuel = [tip(clue) for clue in self.data['C']]
        self.cuel_current = [-1] * len(self.cuel) # -1是未被获取的线索
        self.pswd = self.data['password']
        # result不知道是什么，暂时丢弃

    def cuel_amount(self):
        return len(self.cuel)
    
    def cuel_get(self):
        idx = self.cuel_current.index(-1)
        self.cuel_current[idx] = 0
        return self.cuel[idx].msg()