class ScopedDict:

    def __push__(self):
        self.mydict.append({})

    def __pop__(self):
        self.mydict.pop()

    def __init__(self):
        self.mydict = [{}]

    def __setitem__(self, key, value):
        self.mydict[-1].update({key: value})

    def __getitem__(self, key):
        return next((x for x in reversed(self.mydict) if key in x), {}).get(key, None)

    def __str__(self):
        return str(self.mydict)
    
    def in_scope(self, key):
        return key in self.mydict[-1]

