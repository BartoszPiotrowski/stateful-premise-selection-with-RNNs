import os, sys, subprocess, tempfile, shutil, argparse, uuid
from time import strftime
from joblib import Parallel, delayed


PATH_TO_EPROVER = os.environ['EPROVER']

CPU_TIME=10
MEMORY_LIMIT=2000

def read_lines(file):
    with open(file, 'r') as f:
        return f.read().splitlines()

def append_lines(list_of_lines, file):
    with open(file, mode='at') as f:
        for line in list_of_lines:
            f.write(line + '\n')

#def read_deps(file):
#    '''
#    Returns dictionary of the form:
#        conj1: [deps1, deps2, ...]
#        conj2: [deps7, deps4, ...]
#        ...
#    '''
#    deps = {}
#    for line in read_lines(file):
#        conj, ds = line.split(':')
#        ds = ds.split(' ')
#        if not conj in deps:
#            deps[conj] = []
#        if not ds in deps[conj]:
#            deps[conj].append(ds)
#    return deps

def read_deps(file):
    deps = []
    for line in read_lines(file):
        conj, ds = line.split(':')
        ds = ds.split(' ')
        ds = [d for d in ds if d != '']
        if ds and not (conj, ds) in deps:
            deps.append((conj, ds))
    return deps

def read_statements(file):
    '''
    file should contain lines of the form:
        fof(name,type,formula).
    '''
    stms = {}
    for line in read_lines(file):
        line = line.replace(' ', '')
        name = line.split('(')[1].split(',')[0]
        assert name not in stms
        stms[name] = line
    return stms

def read_statements_2(file):
    '''
    file should contain lines of the form:
        name@fof(name,type,formula).
    '''
    stms = {}
    for line in read_lines(file):
        name,rest = line.split('@')
        #assert name not in stms
        stms[name] = rest
    return stms

class Logger():
    def __init__(self, logfile, silent=False):
        self.logfile = logfile
        self.silent = silent

    def print(self, message):
        t = strftime('%Y-%m-%d--%H:%M:%S')
        m = f"[{t}] {message}"
        if not self.silent:
            print(m)
        with open(self.logfile, 'a') as f:
            f.write(m + '\n')

def problem_file(conj, list_of_deps, statements_file, dir_path, format_2=False):
    if format_2:
        statements = read_statements_2(statements_file)
    else:
        statements = read_statements(statements_file)
    uuid4 = uuid.uuid4().hex
    input_filename = os.path.join(dir_path, uuid4 + '.E_input')
    with open(input_filename, 'w') as problem:
        print(statements[conj].replace('axiom,', 'conjecture,'), file=problem)
        for p in list_of_deps:
            print(statements[p], file=problem)
    return input_filename


def run_E_prover(input_filename, output_filename):
    output = open(output_filename, 'w')
    subprocess.call([
        PATH_TO_EPROVER,
        '--free-numbers',
        '-s',
        '-R',
        '--cpu-limit=' + str(CPU_TIME),
        '--memory-limit=' + str(MEMORY_LIMIT),
        '--print-statistics',
        '-p',
        '--tstp-format',
        input_filename],
        stdout=output, stderr = open(os.devnull, 'w'))
    output.close()


def find_proof(conj, deps, statements_file, dir_path, logger, format_2):
    assert not conj in set(deps), (conj, deps)
    input_filename = problem_file(conj, deps, statements_file, dir_path,
                                  format_2)
    output_filename = input_filename.replace('input', 'output')
    run_E_prover(input_filename, output_filename)
    if "# Proof found!" in read_lines(output_filename):
        logger.print('PROVED#' + conj + ':' + ' '.join(deps) \
                     + '#Output: ' + output_filename)
        return True
    else:
        logger.print('NOT proved#' + conj + ':' + ' '.join(deps) \
                     + '#Output: ' + output_filename)
        return False


# wrapper useful for saving more info when doing parallelization
def find_proof_wrapper(c, ds, st, di, lo, fo):
    return (c, ds, find_proof(c, ds, st, di, lo, fo))


def atp_eval(deps_file, statements_file, dir_path=None, logger=None,
             format_2=False, n_jobs=-1):
    deps = read_deps(deps_file)
    with Parallel(n_jobs=n_jobs) as parallel:
        dfp = delayed(find_proof_wrapper)
        proven = parallel(dfp(c, ds, statements_file, dir_path, logger,
                              format_2) for c, ds in deps)
    return proven


parser = argparse.ArgumentParser()
parser.add_argument('dependencies', type=str)
parser.add_argument('statements', type=str)
parser.add_argument('--dir_for_proofs', type=str, default=None)
parser.add_argument('--format_2', action='store_true')
parser.add_argument('--silent', action='store_true')
args = parser.parse_args()

dir_path = args.dir_for_proofs
if dir_path:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    remove_after = False
else:
    dir_path = tempfile.mkdtemp()
    remove_after = True
log_path = dir_path + '.log'
logger = Logger(log_path, args.silent)

logger.print('ATP evaluation started...')
logger.print(f'Dependencies from: {args.dependencies}')
logger.print(f'Proofs saved to: {dir_path}')
logger.print(f'Logs saved to: {log_path}')

atp_output = atp_eval(args.dependencies, args.statements, dir_path, logger,
                      args.format_2)

# Some statistics about this run:
n_all_attempts = len(atp_output)
conjs = set([r[0] for r in atp_output])
n_conjs= len(conjs)
conjs_n_proofs = [(c,sum([r[2] for r in atp_output if r[0] == c])) for c in conjs]
n_succ_attempts = sum([r[2] for r in atp_output])
n_proved_conjs = sum([bool(r[1]) for r in conjs_n_proofs])
prop_succ_attempts = round(n_succ_attempts / n_all_attempts, 2)
prop_proved_conjs = round(n_proved_conjs / n_conjs, 2)

logger.print(f'Number of all proofs attempts: {n_all_attempts}')
logger.print(f'Number of different conjectures: {n_conjs}')
logger.print(f'Number of successful attempts: '
             f'{n_succ_attempts} ({prop_succ_attempts})')
logger.print(f'Number of proved conjectures: '
             f'{n_proved_conjs} ({prop_proved_conjs})')
logger.print('ATP evaluation finished.\n')

if remove_after:
    shutil.rmtree(dir_path)
