class ScopedDict:

    def __push__(self):
        self.scope_level += 1
        self.dict[self.scope_level] = dict()

    def __pop__(self):
        self.scope_level -= 1   
        self.dict.pop(self.scope_level, None)

    def __init__(self):
        self.dict = dict()
        self.scope_level = 0
        self.dict[self.scope_level] = dict()

    def __setitem__(self, key, value):
        self.dict[self.scope_level][key] = value

    def __getitem__(self, key):
        print(self.dict[self.scope_level][key])
        if self.dict[self.scope_level][key] is not None:
            return self.dict[self.scope_level][key]
        else:
            while self.scope_level > 0:
                if self.dict[self.scope_level][key] is not None:
                    return self.dict[self.scope_level][key]
                self.scope_level -= 1
            raise KeyError(f"Variable {key} not found in any scope")

    def __in__(self, key):
            if self.dict[self.scope_level][key] is not None:
                return True
            else:
                while self.scope_level > 0:
                    if self.dict[self.scope_level][key] is not None:
                        return True
                    self.scope_level -= 1
                return False

