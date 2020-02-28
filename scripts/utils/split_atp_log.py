import sys

log = sys.argv[1]

def read_lines(filename):
    with open(filename, encoding ='utf-8') as f:
        return f.read().splitlines()

log_lines = read_lines(log)
eval_logs = []
starts, ends = [], []
for i in range(len(log_lines)):
    if 'ATP evaluation started' in log_lines[i]:
        starts.append(i)
    if 'ATP evaluation finished' in log_lines[i]:
        ends.append(i)

for end in ends:
    start = max([s for s in starts if s < end])
    one_eval_log_lines = log_lines[start:end+1]
    assert 'Dependencies from: ' in one_eval_log_lines[1]
    deps = one_eval_log_lines[1].split('Dependencies from: ')[1]
    deps_log = deps + '.log'
    deps_proved = deps + '.proved'
    deps_not_proved = deps + '.not_proved'
    print(deps_log)
    print(deps_proved)
    print(deps_not_proved)
    with open(deps_log, 'w') as f:
        f.write('\n'.join(one_eval_log_lines) + '\n')
    one_eval_proved_lines = [l.split('#')[1]
                             for l in one_eval_log_lines if 'PROVED' in l]
    one_eval_not_proved_lines = [l.split('#')[1]
                                 for l in one_eval_log_lines if 'NOT' in l]
    with open(deps_proved, 'w') as f:
        f.write('\n'.join(one_eval_proved_lines) + '\n')
    with open(deps_not_proved, 'w') as f:
        f.write('\n'.join(one_eval_not_proved_lines) + '\n')




