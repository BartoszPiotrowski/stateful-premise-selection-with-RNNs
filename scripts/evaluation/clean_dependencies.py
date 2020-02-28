import sys, os

if __name__ == '__main__':
    deps_file = sys.argv[1]
    with open(deps_file, 'r') as f:
        deps_lines = f.read().splitlines()
    for line in deps_lines:
        conj, ds = line.split(':')
        ds = ds.split(' ')
        ds = [d for d in ds if not d == conj]
        print(f"{conj}:{' '.join(ds)}")

