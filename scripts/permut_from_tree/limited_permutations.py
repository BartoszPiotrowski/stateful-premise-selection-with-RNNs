import os
import sys
import random
random.seed(541)
import itertools
sys.path.append('.')
from utils.proof_to_tree import parse_tptp_proof, build_tree, build_compact_tree



def root(tree):
    #print(list(tree)[0])
    return list(tree)[0]

def children(tree):
    return tree[list(tree)[0]]

def tree_to_seq(tree):
    if not children(tree):
        return [root(tree)]
    else:
        return list(itertools.chain(*[tree_to_seq(st) for st in children(tree)]))

#print(tree_to_seq(tree))


def tree_to_random_seq(tree):
    if not children(tree):
        return [root(tree)]
    else:
        cn = children(tree)
        random_permut = list(random.sample(cn, len(cn)))
        return list(itertools.chain(*[tree_to_random_seq(st) for st in random_permut]))


def tree_to_random_seq_clean(tree):
    seq = tree_to_random_seq(tree)
    print(seq)
    seq_clean = [seq[0]]
    for i in seq:
        if i != seq_clean[-1]:
            seq_clean.append(i)
    return seq_clean


def generate_random_permutations(proof_file, N):
    deps, axioms, conj = parse_tptp_proof(proof_file)
    if len(axioms) > 20:
        return [] # why??
    assert len(conj) == 1
    conj = conj[0]
    tree = build_tree('FALSE', deps)
    permuts = []
    for _ in range(N):
        seq = tree_to_random_seq(tree)
        seq_no_conj = [s for s in seq if s != conj]
        seq_no_conj = [s for s in seq_no_conj if s in axioms]
        if not seq_no_conj:
            return []
        seq_clean = [seq_no_conj[0]]
        for i in seq_no_conj:
            if i != seq_clean[-1]:
                seq_clean.append(i)
        assert set(seq_clean) <= set(axioms)
        if seq_clean not in permuts:
            permuts.append(seq_clean)
        conj_permuts = [conj + ':' + ' '.join(p) for p in permuts]
    return conj_permuts



#deps, axioms, conjectures = parse_tptp_proof(proof_file)
#tree = build_compact_tree('FALSE', deps)
#tree = build_tree('FALSE', deps)
#print(tree_to_random_seq_clean(tree))
#print(tree_to_seq(tree))



indir = sys.argv[1]
N = int(sys.argv[2])
outfile = sys.argv[3]

for proof_file in os.listdir(indir):
    proof_file = indir + '/' + proof_file
    print(proof_file)
    ps = generate_random_permutations(proof_file, N)
    with open(outfile, 'a') as f:
        for p in ps:
            f.write(p + '\n')


