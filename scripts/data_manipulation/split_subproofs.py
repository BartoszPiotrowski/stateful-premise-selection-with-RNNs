import sys

subproofs_all = sys.argv[1]
sublemmas_provable = sys.argv[2]
sublemmas_names = sys.argv[3]
files_subset = sys.argv[4]
max_height = int(sys.argv[5])

def read_lines(filename):
    with open(filename, encoding ='utf-8') as f:
        return f.read().splitlines()

subproofs_all_lines = read_lines(subproofs_all)
sublemmas_names_lines = read_lines(sublemmas_names)
sublemmas_provable = set(read_lines(sublemmas_provable))
files_subset = set(read_lines(files_subset))

sublemmas_names = {}
for line in sublemmas_names_lines:
    name, tptp = line.split('#')
    assert tptp not in sublemmas_names
    sublemmas_names[tptp] = name

for line in subproofs_all_lines:
    tptp, deps, height, file = line.split('#')
    height = int(height)
    if tptp in sublemmas_names:
        name = sublemmas_names[tptp]
        if name in sublemmas_provable \
           and file in files_subset \
           and height <= max_height:
            print(f"{name}:{deps}#{height}")

