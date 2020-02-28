
mkdir data/testing

for l in `cat data/split/theorems_test`; do
	grep $l@ data/statements/standard >> data/testing/tmp.tptp; done
cut -d@ -f1 data/testing/tmp.tptp > data/testing/names
cut -d@ -f2 data/testing/tmp.tptp > data/testing/statements.standard

for l in `cat data/split/theorems_test`; do
	grep $l@ data/statements/prefix >> data/testing/tmp.prefix; done
cut -d@ -f2 data/testing/tmp.prefix > data/testing/statements.prefix
rm -f data/testing/tmp*

python3 scripts/data_manipulation/unions_of_dependencies.py \
	data/split/dependencies_test > data/testing/dependencies.unions
