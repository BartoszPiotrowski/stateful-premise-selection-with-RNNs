import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('deps', type=str)
    parser.add_argument('--sep', type=str, default=':')
    args = parser.parse_args()

    with open(args.deps, 'r') as f:
        deps_lines = f.read().splitlines()

    deps_unions ={}
    for line in deps_lines:
        thm_name, ds = line.split(args.sep)
        ds = ds.split(' ')
        if thm_name not in deps_unions:
            deps_unions[thm_name] = set()
        deps_unions[thm_name].update(ds)

    for thm_name in deps_unions:
        ds = ' '.join(deps_unions[thm_name])
        print(f"{thm_name}{args.sep}{ds}")

