import numpy as np
from random import shuffle, seed
import argparse
import sys
seed(541)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('deps', type=str)
    parser.add_argument('stms', type=str)
    parser.add_argument('--output_prefix', type=str)
    parser.add_argument('--num_permut', type=int, default=0)
    parser.add_argument('--oversampling_premises', type=str, default=None)
    parser.add_argument('--oversampling_theorems', type=str, default=None)
    parser.add_argument('--oversampling_premises_2', type=str, default=None)
    parser.add_argument('--oversampling_theorems_2', type=str, default=None)
    args = parser.parse_args()

    with open(args.deps, 'r') as f:
        deps_lines = f.read().splitlines()

    with open(args.stms, 'r') as f:
        stms_lines = f.read().splitlines()
    stms = {s.split('@')[0]: s.split('@')[1] for s in stms_lines}

    # oversampling_*_3
    def oversampling_ratios(dict_of_counts):
        BINS = 10
        bins = {}
        values = list(dict_of_counts.values())
        for i in range(2, BINS):
            quantile_high = np.quantile(values, 0.5 - (0.5 / BINS) * i)
            quantile_low = np.quantile(values,  0.5 - (0.5 / BINS) * (i + 1))
            bins[i] = (quantile_high, quantile_low)
        dict_of_rations = {it:1 for it in dict_of_counts}
        for item in dict_of_counts:
            for i in bins:
                if bins[i][0] >= dict_of_counts[item] >= bins[i][1]:
                    dict_of_rations[item] = i
        assert set(dict_of_counts) == set(dict_of_rations)
        return dict_of_rations

    # oversampling_*_2
    #def oversampling_ratios(dict_of_counts):
    #    BINS = 10
    #    bins = {}
    #    values = list(dict_of_counts.values())
    #    for i in range(1, BINS):
    #        quantile_high = np.quantile(values, 1 / i)
    #        quantile_low = np.quantile(values, 1 / (i + 1))
    #        bins[i] = (quantile_high, quantile_low)
    #    bins[BINS] = (bins[BINS - 1][1], 0)
    #    dict_of_rations = {}
    #    for item in dict_of_counts:
    #        for i in bins:
    #            if bins[i][0] >= dict_of_counts[item] >= bins[i][1]:
    #                dict_of_rations[item] = i
    #    assert set(dict_of_counts) == set(dict_of_rations)
    #    return dict_of_rations


    if args.oversampling_premises_2:
        with open(args.oversampling_premises_2, 'r') as f:
            premises_counts_lines = f.read().splitlines()
        premises_counts = {}
        for line in premises_counts_lines:
            p, c = line.split(' ')
            premises_counts[p] = int(c)
        lists_of_deps_avg_counts = {}
        for line in deps_lines:
            conj, ds_nonsplit = line.split(':')
            ds = ds_nonsplit.split(' ')
            counts = [premises_counts[d] for d in ds]
            avg_counts = np.mean(counts)
            lists_of_deps_avg_counts[ds_nonsplit] = avg_counts
        dict_of_ratios = oversampling_ratios(lists_of_deps_avg_counts)

    if args.oversampling_theorems_2:
        with open(args.oversampling_theorems_2, 'r') as f:
            words_counts_lines = f.read().splitlines()
        words_counts = {}
        for line in words_counts_lines:
            p, c = line.split(' ')
            words_counts[p] = int(c)
        words = set(words_counts)
        stms_avg_counts = {}
        for line in deps_lines:
            conj, _ = line.split(':')
            conj_stm = stms[conj].split(' ')
            conj_words = [w for w in conj_stm if w in words]
            counts = [words_counts[w] for w in conj_words]
            avg_counts = np.mean(counts)
            stms_avg_counts[conj] = avg_counts
        dict_of_ratios = oversampling_ratios(stms_avg_counts)


    if args.oversampling_premises:
        with open(args.oversampling_premises, 'r') as f:
            premises_counts_lines = f.read().splitlines()
        premises_counts = {}
        for line in premises_counts_lines:
            p, c = line.split(' ')
            premises_counts[p] = int(c)
        avg_premises_count = np.mean(list(premises_counts.values()))

    if args.oversampling_theorems:
        with open(args.oversampling_theorems, 'r') as f:
            theorems_counts_lines = f.read().splitlines()
        theorems_counts = {}
        for line in theorems_counts_lines:
            p, c = line.split(' ')
            theorems_counts[p] = int(c)
        avg_theorems_count = np.mean(list(theorems_counts.values()))

    source_lines, target_lines, names_lines = [], [], []
    for line in deps_lines:
        conj, ds_nonsplit = line.split(':')
        ds = ds_nonsplit.split(' ')
        if args.num_permut:
            # permute dependencies randomly
            for i in range(args.num_permut):
                shuffle(ds)
                target_lines.append(' '.join(ds))
                source_lines.append(stms[conj])
                names_lines.append(conj)
        elif args.oversampling_premises and not args.oversampling_theorems:
            conj_premises_counts = [premises_counts[d] for d in ds]
            conj_premises_inv_counts = [avg_premises_count / p_c
                                       for p_c in conj_premises_counts]
            avg_conj_premises_inv_counts = \
                    sum(conj_premises_inv_counts)
            n_oversampling = int(round(avg_conj_premises_inv_counts))
            if n_oversampling == 0:
                n_oversampling = 1
            for _ in range(n_oversampling):
                target_lines.append(' '.join(ds))
                source_lines.append(stms[conj])
                names_lines.append(conj)
        elif not args.oversampling_premises and args.oversampling_theorems:
            conj_inv_count = avg_theorems_count / theorems_counts[conj]
            n_oversampling = int(round(conj_inv_count))
            if n_oversampling == 0:
                n_oversampling = 1
            for _ in range(n_oversampling):
                target_lines.append(' '.join(ds))
                source_lines.append(stms[conj])
                names_lines.append(conj)
        elif args.oversampling_premises and args.oversampling_theorems:
            conj_inv_count = avg_theorems_count / theorems_counts[conj]
            conj_premises_counts = [premises_counts[d] for d in ds]
            conj_premises_inv_counts = [avg_premises_count / p_c
                                       for p_c in conj_premises_counts]
            avg_conj_premises_inv_counts = \
                    sum(conj_premises_inv_counts)
            n_oversampling = \
                    int(round(avg_conj_premises_inv_counts * conj_inv_count))
            if n_oversampling == 0:
                n_oversampling = 1
            for _ in range(n_oversampling):
                target_lines.append(' '.join(ds))
                source_lines.append(stms[conj])
                names_lines.append(conj)
        elif args.oversampling_premises_2:
            for _ in range(dict_of_ratios[ds_nonsplit]):
                target_lines.append(' '.join(ds))
                source_lines.append(stms[conj])
                names_lines.append(conj)
        elif args.oversampling_theorems_2:
            for _ in range(dict_of_ratios[conj]):
                target_lines.append(' '.join(ds))
                source_lines.append(stms[conj])
                names_lines.append(conj)
        else:
            target_lines.append(' '.join(ds))
            source_lines.append(stms[conj])
            names_lines.append(conj)


    target_file = args.output_prefix + '.tgt'
    source_file = args.output_prefix + '.src'
    names_file = args.output_prefix + '.names'

    with open(source_file, 'w') as f:
        for line in source_lines:
            f.write(line + '\n')
    with open(target_file, 'w') as f:
        for line in target_lines:
            f.write(line + '\n')

