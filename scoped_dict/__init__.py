class ScopedDict:
    scope_level = 0

    def __push__(self):
        self.scope_level += 1

    def __pop__(self):
        self.scope_level -= 1   

    def __init__(self):
        self = dict()

    def __setitem__(self, name, value):
        self[self.scope_level][name] = value

    def __getitem__(self, name):
        if self[self.scope_level][name] is not None:
            return self[self.scope_level][name]
        else:
            while self.scope_level > 0:
                if self[self.scope_level][name] is not None:
                    return self[self.scope_level][name]
                self.scope_level -= 1
            raise KeyError(f"Variable {name} not found in any scope")

    def __in__(self, name):
            if self[self.scope_level][name] is not None:
                return True
            else:
                while self.scope_level > 0:
                    if self[self.scope_level][name] is not None:
                        return True
                    self.scope_level -= 1
                return False

