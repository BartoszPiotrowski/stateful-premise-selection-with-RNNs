import sys, os

def deps_from_proof(file_with_proof):
    '''
    Extracts dependecies (axioms/premises) from a given proof file.
    The order of extracted premises is induced by the order of appearance
    of the premises in inferences saved in the proof file.
    '''
    with open(file_with_proof, 'r') as f:
        lines = f.read().splitlines()

    if "# Proof found!" in lines and "# SZS status Theorem" in lines:
        lines = [l for l in lines if l and not l[0] == '#']
        lines = [l.replace(' ', '') for l in lines]
        premises_unordered = set()
        all_clauses_names = set()
        conjecture = None
        for l in lines:
            l = l.replace(' ', '')
            all_clauses_names.add(l.split('(')[1].split(',')[0])
            if ',file(' in l:
                name = l.split(',')[0].split('(')[1]
                if ',conjecture,' in l:
                    assert conjecture == None # it can only be one conjecture
                    conjecture = name
                elif ',axiom,' in l or ',lemma,' in l:
                    premises_unordered.add(name)
                else:
                    raise ValueError(
                        'Each line of proof file containing name of file'
                        ' needs to contain either axiom, lemma or conjecture')

        # loop to rename premises according to a chain of single-argument
        # inferences -- to make order follow "real" usage of premises
        def parent_children(line, clauses_names):
            line_aux = line.replace('[', ',').replace(']', ',')
            line_aux = line_aux.replace('(', ',').replace(')', ',')
            children_names = clauses_names.intersection(line_aux.split(','))
            parent_name = line.split('(')[1].split(',')[0]
            return parent_name, list(children_names)
        new_names_premises = {p: p for p in premises_unordered}
        change_indicator = True
        while change_indicator:
            change_indicator = False
            clauses_new_names = {}
            for line in lines:
                if 'inference(' in line:
                    parent, children = parent_children(line, all_clauses_names)
                    if len(children) == 1:
                        premises_children = \
                            list(set(new_names_premises).intersection(children))
                        if premises_children:
                            child_premise = premises_children[0]
                            if not child_premise in clauses_new_names:
                                clauses_new_names[child_premise] = []
                            clauses_new_names[child_premise].append(parent)
                            change_indicator = True
            #new_names_premises[result_name] = new_names_premises[premise]
            # Updating "new names" of premises
            for name in clauses_new_names:
                if name in new_names_premises:
                    for new_name in clauses_new_names[name]:
                        new_names_premises[new_name] = \
                                new_names_premises[name]
                    del new_names_premises[name]
        premises_new_names = set(new_names_premises)
        # end of finding "new names" for premises; they are in new_names_premises

        premises_ordered = []
        for line in lines:
            line = line.replace(' ', '')
            if 'inference(' in line:
                _, line_clauses = parent_children(line, all_clauses_names)
                line_premises = premises_new_names.intersection(line_clauses)
                premises_ordered.extend(line_premises)
                premises_new_names.difference_update(line_premises)
        premises_ordered = [new_names_premises[p] for p in premises_ordered]
        assert set(premises_ordered) == set(premises_unordered)
        return conjecture, premises_ordered
    else:
        return None

if __name__ == '__main__':
    proof_dir = sys.argv[1]
    for f in os.listdir(proof_dir):
        conjecture_premises = deps_from_proof(os.path.join(proof_dir, f))
        if conjecture_premises:
            conjecture, premises = conjecture_premises
            #premises.sort()
            print(f"{conjecture}:{' '.join(premises)}")

