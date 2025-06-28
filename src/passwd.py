import hashlib
import json


def encrypt(string: str) -> str:
    salt = b'\xb2S"e}\xdf\xb0\xfe\x9c\xde\xde\xfe\xf3\x1d\xdc>'
    string_bytes = string.encode('utf-8')
    hash_obj = hashlib.sha256(salt + string_bytes)
    return hash_obj.hexdigest()


def verify(string: str, hash_value: str) -> bool:
    print(encrypt(string))
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

        if self.data['C'] == None or self.data['L'] == None:
            raise ValueError("invalid file")

        self.hash = self.data['L']
        self.clue = [tip(clue) for clue in self.data['C']]
        self.clue_current = [-1] * len(self.clue) # -1是未被获取的线索

        # self.pswd = self.data['password']
        

    def clue_amount(self):
        return len(self.clue)
    
    def clue_get(self):
        idx = self.clue_current.index(-1)
        self.clue_current[idx] = 0
        return self.clue[idx].msg()
    
    def crack(self):
        self.prime = False
        self.prime_list = [2, 3, 5, 7]
        self.odd = [-1, -1, -1]
        self.pwd = [-1,-1,-1]
        self.tries = 0
        self.completed = False
        
        # known clues list
        self.clues = []
        for i in range(len(self.clue_current)):
            if self.clue_current[i] == 0:
                self.clues.append(self.clue[i].data())
        
        # analyse clues
        for i in range(len(self.clues)):
            if len(self.clues[i]) == 2:
                if self.clues[i][1] == -1:
                    self.prime = True
                elif self.clues[i][1] == 0:
                    self.odd[self.clues[i][0]-1] = 0
                elif self.clues[i][1] == 1:
                    self.odd[self.clues[i][0]-1] = 1
            elif len(self.clues[i]) == 3:
                for j in range(len(self.clues[i])):
                    if self.clues[i][j] == -1:
                        continue
                    else:
                        self.pwd[j] = self.clues[i][j]
        current = [-1, -1, -1]
        self._backtrack(current, 0)
        return('password:'+''.join(map(str, self.results)))

    def _backtrack(self, current, index):
        possible_digits = list(range(10))
        if self.pwd[index] != -1:
            possible_digits = [self.pwd[index]]
        else:
            if self.prime:
                possible_digits = self.prime_list
            if not self.odd[index] == -1:
                possible_digits = [d for d in possible_digits if (d % 2) == self.odd[index]]
        
                
        for digit in possible_digits:
            if self.completed:
                return
            if self.prime:
                used = False
                for j in range(index):
                    if digit == current[j]:
                        used = True
                        break
                if used:
                    continue
            
            current[index] = digit
            if index == 2:
                if verify(''.join(map(str, current)), self.hash):
                    self.results = current.copy()
                    self.completed = True
                else:
                    self.tries += 1
            else:
                self._backtrack(current, index + 1)
                if self.completed:
                    return