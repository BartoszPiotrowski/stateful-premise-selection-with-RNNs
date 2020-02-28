import argparse


parser = argparse.ArgumentParser()
parser.add_argument('proved', type=str)
parser.add_argument('not_proved', type=str)
parser.add_argument('heights', type=str, default=None)
parser.add_argument('--sep', type=str, default=':')
args = parser.parse_args()

with open(args.proved, 'r') as f:
    proved_lines = f.read().splitlines()

with open(args.not_proved, 'r') as f:
    not_proved_lines = f.read().splitlines()

with open(args.heights, 'r') as f:
    heights_lines = f.read().splitlines()


proved = {l.split(':')[0] for l in proved_lines}
not_proved = {l.split(':')[0] for l in not_proved_lines}
evaluated = proved | not_proved

print(f'Proved: {len(proved)}/{len(evaluated)}'
      f' ({len(proved) / len(evaluated):.3f})\n')

if args.heights:
    heights = {}
    max_height = 0
    for l in heights_lines:
        n, h = l.split(args.sep)
        h = int(h)
        if h > max_height:
            max_height = h
        if not n in heights:
            heights[n] = []
        heights[n].append(h)
    heights_avg = {}
    for n in heights:
        heights_avg[n] = sum(heights[n]) / len(heights[n])

    for i in range(max_height):
        lem_h = {n for n in heights_avg if i < heights_avg[n] <= i + 1}
        proved_h = lem_h & proved
        not_proved_h = lem_h & not_proved
        evaluated_h = proved_h | not_proved_h
        if proved_h:
            print(f'Height: ({i},{i+1}]')
            print(f'Number of lemmas: {len(evaluated_h)}')
            print(f'Proved: {len(proved_h)}/{len(evaluated_h)}'
                  f' ({len(proved_h)/len(evaluated_h):.3f})')
            print()


