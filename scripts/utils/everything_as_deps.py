import sys

theorems = sys.argv[1]
chronology = sys.argv[2]

def read_lines(filename):
    with open(filename, encoding ='utf-8') as f:
        return f.read().splitlines()

theorems = read_lines(theorems)
chronology = read_lines(chronology)

for t in theorems:
    t_index = chronology.index(t)
    print(f"{t}:{' '.join(chronology[:t_index])}")
