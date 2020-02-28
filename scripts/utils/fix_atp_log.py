import sys

log = sys.argv[1]

def read_lines(filename):
    with open(filename, encoding ='utf-8') as f:
        return f.read().splitlines()

log_lines = read_lines(log)

i = 0
while i < len(log_lines):
    l = log_lines[i].strip(' ')
    if l and l[-1] == ':':
        l_next = log_lines[i + 1].strip(' ')
        l_next_bare = l_next.split(']')[1].strip(' ')
        print(l + ' ' + l_next_bare)
        i += 2
    else:
        print(l)
        i += 1
