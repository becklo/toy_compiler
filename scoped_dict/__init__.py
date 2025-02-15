class ScopedDict:

    def __push__(self):
        self.mydict.append({})

    def __pop__(self):
        self.mydict.pop()

    def __init__(self):
        self.mydict = [{}]

    def __setitem__(self, key, value):
        print(self.mydict)
        self.mydict[-1].update({key: value})

    def __getitem__(self, key):
        return next((x for x in reversed(self.mydict) if key in x), {}).get(key, None)

    def __str__(self):
        return str(self.mydict)

