import sys

proved = sys.argv[1]
not_proved = sys.argv[2]

def read_lines(filename):
    with open(filename, encoding ='utf-8') as f:
        return f.read().splitlines()

proved_lines = read_lines(proved)
not_proved_lines = read_lines(not_proved)

proved = {}
for l in proved_lines:
    t, ds = l.split(':')
    ds = ds.split(' ')
    if t not in proved:
        proved[t] = []
    proved[t].append(set(ds))

not_proved = {}
for l in not_proved_lines:
    t, ds = l.split(':')
    ds = ds.split(' ')
    if t not in not_proved:
        not_proved[t] = []
    not_proved[t].append(set(ds))

for t in proved:
    if t in not_proved:
        for ds in proved[t]:
            for n_ds in not_proved[t]:
                if ds < n_ds:
                    print('PROVED    : ' + t + ':' + ' '.join(ds))
                    print('NOT proved: ' + t + ':' + ' '.join(n_ds))

