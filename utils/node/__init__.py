class Node:
    def __init__(self, type, value, children=[]):
        self.type = type
        self.value = value
        self.children = children

    def pretty_print(self, node, indent=0):
        print_string = '  '* indent
        print_string += str(node.type) +' : '
        if str(node.type) == '='  and len(node.value) == 2:
            print_string += '(' + str(node.value[0]) +') ' + str(node.value[1]) +' '
        else:
            print_string += str(node.value) +' '

        for child in node.children:
            print_string += '\n' + self.pretty_print(child, indent+1)

        return print_string
    
    def __str__(self):
        return self.pretty_print(self)

