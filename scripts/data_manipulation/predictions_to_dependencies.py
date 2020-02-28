import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('deps', type=str)
    parser.add_argument('thms_names', type=str)
    parser.add_argument('--only_unions', action='store_true')
    parser.add_argument('--sep', type=str, default=':')
    args = parser.parse_args()

    with open(args.deps, 'r') as f:
        deps_lines = f.read().splitlines()

    with open(args.thms_names, 'r') as f:
        thms_names = f.read().splitlines()

    assert len(deps_lines) % len(thms_names) == 0
    # when we produced n translations per theorem:
    n = int(len(deps_lines) / len(thms_names))
    if n > 1:
        thms_names = [t for t in thms_names for _ in range(n)]
        assert thms_names[0] == thms_names[1]

    deps_unions = {conj: set() for conj in thms_names}
    for i in range(len(deps_lines)):
        conj = thms_names[i]
        ds = deps_lines[i].split(' ')
        ds = [d for d in ds if not d == conj]
        if ds:
            deps_unions[conj].update(ds)
            if not args.only_unions:
                print(f"{conj}{args.sep}{' '.join(ds)}")

    for conj in deps_unions:
        ds = ' '.join(deps_unions[conj])
        print(f"{conj}{args.sep}{ds}")



