import sys
import re
import graphviz

def main():
    """ Parse a file and produces a dot file """
    
    infile = sys.argv[1] if len(sys.argv) > 1 else 'parser.out'
    
    state = None
    
    dot = graphviz.Digraph(comment=infile, format='pdf')
    dot.size = '1000,1000'

    with open(infile, 'r') as f:
        lines = f.readlines()
        nodetext = ''
        for line in lines:
            if line.startswith('state '):
                if state is not None:
                    dot.node(state, nodetext, shape='box')
                    nodetext = ''
                state = line.split()[1]
                nodetext += f'State: {state}\n\n'
            if state is not None and len(line)>5 and line[0:4] == '    ':
                nodetext += line.strip()+'\n'
            if state is not None and 'shift and go to state' in line:
                next_state = re.search(r'go to state (\d+)', line).group(1)
                label_state = re.search(r'(\S+)\s+shift and go to state \d+', line).group(1)
                dot.edge(state, next_state, label=label_state)
        if state is not None: # In case we have uncleared state
            dot.node(state, nodetext, shape='box')
                
    v = dot.unflatten(stagger=20, fanout=2, chain=2)
    v.render(f'{infile}.dot', view=False)

if __name__ == '__main__':
    main()
