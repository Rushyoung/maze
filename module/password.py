import json
from Lock import PasswordLock

class PwdLocker:
    def __init__(self, data) ->None :
        self.lock = PasswordLock()
        if data['C'] == None or data['L'] == None:
            print("invaild file")
        
        self.prime = False
        self.prime_list = [2, 3, 5, 7]
        self.odd = [-1, -1, -1]
        self.pwd = [-1,-1,-1]
        self.hash = data["L"]
        self.tries = 0
        self.completed = False
        clue = data['C']
        for i in range(len(clue)):
            if len(clue[i]) == 2:
                if clue[i][1] == -1:
                    self.prime = True
                elif clue[i][1] == 0:
                    self.odd[clue[i][0]-1] = 0
                elif clue[i][1] == 1:
                    self.odd[clue[i][0]-1] = 1
            elif len(clue[i]) == 3:
                for j in range(len(clue[i])):
                    if clue[i][j] == -1:
                        continue
                    else:
                        self.pwd[j] = clue[i][j]
        
    def crack(self):
        current = [-1, -1, -1]
        self._backtrack(current, 0)
        print(''.join(map(str, current)))

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
            else:
                current[index] = digit
            if index == 2:
                if self.lock.verify_password(''.join(map(str, current)), self.hash):
                    self.completed = True
                self.tries += 1
                return
            else:
                self._backtrack(current, index + 1)




                    
        




if __name__ == '__main__':
    with open('pwd.json', 'r') as f:
        data = json.load(f)
    lock = PwdLocker(data)
    lock.crack()
    print(lock.tries)
    
    
    

    

    



                
    