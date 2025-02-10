class ScopedDict:

    def __push__(self):
        self.scope_level += 1
        self.mydict.append(self.scope_level)
        self.mydict[self.scope_level] = []

    def __pop__(self):
        self.scope_level -= 1   
        self.mydict.pop(self.scope_level)

    def __init__(self):
        self.mydict = []
        self.scope_level = 0
        self.mydict.append(self.scope_level)
        self.mydict[self.scope_level] = []

    def __setitem__(self, key, value):
        self.mydict[self.scope_level].append({key: value})

    def __getitem__(self, key):
        return next((x for x in next((x for x in reversed(self.mydict)),{}) if key in x), {}).get(key, None)

    def __str__(self):
        return str(self.mydict)
    # def __in__(self, key):  
    #     v = (x for x in reversed(self.mydict))
    #     next((x for x in v if key in x), {}).get(key, None)
    #         # next((x for x in reversed(self.mydict) if key in x), {}).get(key, None) is not None
