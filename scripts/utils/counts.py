import sys, argparse

DELIMITER = ' '

parser = argparse.ArgumentParser()
parser.add_argument('file', type=str)
parser.add_argument('--split_to_words', action='store_true')
args = parser.parse_args()

with open(args.file) as f:
    lines = f.read().splitlines()

if args.split_to_words:
    atoms = []
    for line in lines:
        atoms.extend(line.split(DELIMITER))
else:
    atoms = lines

atoms_counts = {atom: 0 for atom in set(atoms)}
for atom in atoms:
    atoms_counts[atom] += 1

atoms_counts = list(atoms_counts.items())
atoms_counts.sort(key = lambda x: x[1], reverse = True)

for l,c in atoms_counts:
    print(l, c)



