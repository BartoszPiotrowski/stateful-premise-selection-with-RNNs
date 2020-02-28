import argparse


def jaccard_index(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    return len(set1.intersection(set2)) / len(set1.union(set2))

def coverage(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    c = len(set1.intersection(set2)) / len(set2)
    #if c < 0.01:
    #    print('1:', set1)
    #    print('2:', set2)
    #    print(c)
    #    print()
    return c

parser = argparse.ArgumentParser()
parser.add_argument('deps_true', type=str)
parser.add_argument('deps_predicted', type=str)
parser.add_argument('--sep', type=str, default=':')
parser.add_argument('--heights', type=str, default=None)
args = parser.parse_args()

with open(args.deps_true, 'r') as f:
    deps_true_lines = f.read().splitlines()
deps_true = [l.strip(' ') for l in deps_true_lines]

with open(args.deps_predicted, 'r') as f:
    deps_predicted_lines = f.read().splitlines()
deps_predicted = [l.strip(' ') for l in deps_predicted_lines]

#assert len(deps_true_lines) == len(deps_predicted_lines)

deps_true = {}
for l in deps_true_lines:
    s, d = l.split(args.sep)
    d = set(d.split(' '))
    assert not s in deps_true
    deps_true[s] = d

deps_predicted = {}
for l in deps_predicted_lines:
    s, d = l.split(args.sep)
    d = set(d.split(' '))
    assert not s in deps_predicted
    deps_predicted[s] = d

jaccard_indices = [jaccard_index(deps_predicted[thm], deps_true[thm]) \
                   for thm in set(deps_predicted)]
avg_jaccard_index = sum(jaccard_indices) / len(jaccard_indices)

coverages = [coverage(deps_predicted[thm], deps_true[thm]) \
                   for thm in set(deps_predicted)]
avg_coverage = sum(coverages) / len(coverages)
print('Average Jaccard index: {0:.3f}'.format(avg_jaccard_index))
print('Average coverage: {0:.3f}'.format(avg_coverage))

if args.heights:
    with open(args.heights, 'r') as f:
        heights_lines = f.read().splitlines()
    heights = {}
    max_height = 0
    for line in heights_lines:
        stms, h = line.split(args.sep)
        h = int(h)
        if h > max_height:
            max_height = h
        if not stms in heights:
            heights[stms] = []
        heights[stms].append(h)
    heights_avg = {}
    for stms in heights:
        heights_avg[stms] = sum(heights[stms]) / len(heights[stms])

    for i in range(max_height):
        thms_h = [s for s in heights_avg if i < heights_avg[s] <= i + 1]
        thms_h = [s for s in thms_h if s in set(deps_predicted)]
        if thms_h:
            jaccard_indices = [jaccard_index(deps_predicted[thm],
                                             deps_true[thm]) for thm in thms_h]
            avg_jaccard_index = sum(jaccard_indices) / len(jaccard_indices)

            coverages = [coverage(deps_predicted[thm], deps_true[thm]) \
                               for thm in thms_h]
            avg_coverage = sum(coverages) / len(coverages)
            print(f'Average height in ({i},{i+1}]:')
            print(f'   Number of lemmas: {len(thms_h)}')
            print(f'   Average J. index: {avg_jaccard_index:.3f}')
            print(f'   Average coverage: {avg_coverage:.3f}')
            print()

