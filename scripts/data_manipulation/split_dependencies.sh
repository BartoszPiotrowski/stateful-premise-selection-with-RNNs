#!/usr/bin/bash


rm -f data/split/dependencies*
rm -f data/split/premises*

for l in `cat data/split/theorems_train`
do grep $l: data/dependencies_from_proofs >> data/split/dependencies_train
done

for l in `cat data/split/theorems_test`
do grep $l: data/dependencies_from_proofs >> data/split/dependencies_test
done

cat data/dependencies_from_proofs | cut -d: -f2 | sed 's/ /\n/g' | sort -u \
	> data/split/premises

cat data/split/dependencies_train | cut -d: -f2 | sed 's/ /\n/g' | sort -u \
	> data/split/premises_train

cat data/split/dependencies_test | cut -d: -f2 | sed 's/ /\n/g' | sort -u \
	> data/split/premises_test

# Premises in test not appearing in train
comm -23 data/split/premises_test data/split/premises_train \
	> data/split/premises_test_not_in_train

for p in `cat data/split/premises_test_not_in_train`
do grep $p data/split/dependencies_test >> data/split/tmp
done
sort -u data/split/tmp > data/split/dependencies_test_bad_premises
comm -23 <(sort data/split/dependencies_test) \
		 <(sort data/split/dependencies_test_bad_premises) \
		 > data/split/dependencies_test_good_premises
mv -f data/split/dependencies_test_good_premises data/split/dependencies_test
cut -d: -f1 data/split/dependencies_test | sort -u > data/split/theorems_test

rm -f data/split/dependencies*_bad*
rm -f data/split/tmp

