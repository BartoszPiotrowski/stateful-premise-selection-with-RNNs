# Stateful Premise Selection with RNNs

This repository contains data and scripts related to the paper
"Stateful Premise Selection with Recurrent Neural Networks"
submitted to LPAR23.

## Requirements
1. Python 3 (version >=3.7)
2. OpenNMT toolkit (available at: https://github.com/OpenNMT/OpenNMT-py)
3. E prover (we used version 2.3, available at: wwwlehre.dhbw-stuttgart.de/~sschulz/WORK/E_DOWNLOAD/V_2.3/E.tgz)

## Initial data
- `data/proofs` -- 24087 E-prover proofs of 1469 theorems from MPTP2078.
- `data/statements/standard` -- tokenized statement in standard TPTP notation.
- `data/statements/prefix` -- tokenized statements in prefix notation.
- `data/statements/standard_full` -- same as `standard`, but in
	`fof(NAME,conjecture,STATEMENT)`
	format (useful during ATP evaluation).
In the first two files with statements name of conjecture/premise is separated
from its statement with `@` symbol.
`data/theorems_from_MPTP2078` -- all 2078 theorems in MPTP2078 data set.

## Dependencies derived from proofs
`data/dependencies_from_proofs` -- contain dependencies extracted from the
	proofs; this file was produced with:
```
python3 scripts/data_manipulation/deps_from_proofs.py data/proofs | sort -u \
	> data/dependencies_from_proofs
```
`data/theorems_from_proofs` -- list of all theorems having at least one proof
	in `data/proofs`; produced with:
```
cut -d: -f1 data/dependencies_from_proofs | sort -u | shuf \
	> data/theorems_from_proofs
```

## Split to training and testing part

We split theorems (and its dependencies) to training and testing part in
proportions 75% and 25%, respectively:
```
mkdir data/split
head -1100 data/theorems_from_proofs > data/split/theorems_train
tail -369 data/theorems_from_proofs  > data/split/theorems_test
comm -12 <(sort data/split/theorems_train) <(sort data/split/theorems_test)
```
Empty output of the last command means no intersection between training and
testing theorems.

Dependencies were split according to `theorems_test`/`theorems_train` split
with additional modification, that examples in testing part containing
premises not present in training examples were removed. It may be reproduced by:
```
./scripts/data_manipulation/split_dependencies.sh
```
`data/split/dependencies_train` and `data/split/dependencies_test` will
contain the desired split.

## Testing data
Now we need to prepare testing data: separate files with statements of testing
theorems and unions of its dependencies (for measuring similarity between
predictions and dependencies from the initial proofs). After running
```
./scripts/data_manipulation/testing_data.sh
```
the directory `data/testing` will contain:
`data/testing/names` is list of names of testing theorems,
`data/testing/statements.standard` and `data/testing/statements.prefix`
	with tokenized statements of the theorems `test.names` in TPTP
	and prefix notation, respectively; this will be input for a trained
	neural model during testing,
`data/testing/dependencies.unions` contains unions of dependencies for all


## Preparation of training data

Below are shown various ways of preparing training data for NMT models,
as described in the paper.

### Target: permuted, source: standard and prefix
```
TRAIN_DATA=data/training/permuted
mkdir -p $TRAIN_DATA
python3 scripts/data_manipulation/training_data.py \
	data/split/dependencies_train \
	data/statements/standard \
	--num_permut 1 \
	--output_prefix $TRAIN_DATA/train_standard
python3 scripts/data_manipulation/training_data.py \
	data/split/dependencies_train \
	data/statements/prefix \
	--num_permut 1 \
	--output_prefix $TRAIN_DATA/train_prefix
```

### Target: permuted_100, source: standard and prefix
```
TRAIN_DATA=data/training/permuted_100
mkdir -p $TRAIN_DATA
python3 scripts/data_manipulation/training_data.py \
	data/split/dependencies_train \
	data/statements/standard \
	--num_permut 100 \
	--output_prefix $TRAIN_DATA/train_standard
python3 scripts/data_manipulation/training_data.py \
	data/split/dependencies_train \
	data/statements/prefix \
	--num_permut 100 \
	--output_prefix $TRAIN_DATA/train_prefix
```

### Target: order_from_proof, source: standard and prefix
```
TRAIN_DATA=data/training/order_from_proof
mkdir -p $TRAIN_DATA
python3 scripts/data_manipulation/training_data.py \
	data/split/dependencies_train \
	data/statements/standard \
	--output_prefix $TRAIN_DATA/train_standard
python3 scripts/data_manipulation/training_data.py \
	data/split/dependencies_train \
	data/statements/prefix \
	--output_prefix $TRAIN_DATA/train_prefix
```

### Oversampling, target: order_from_proof, source: standard

To perform oversampling, first we need to gather statistics on frequency
of premises appearing in training dependencies:
```
python3 scripts/utils/counts.py \
	data/training/order_from_proof/train_standard.tgt \
	--split_to_words \
	> data/training/order_from_proof/train_standard.tgt.counts
```
Using these statistics produce oversampled training data:
```
TRAIN_DATA=data/training/oversampled
mkdir -p $TRAIN_DATA
python3 scripts/data_manipulation/training_data.py \
	data/split/dependencies_train \
	data/statements/standard \
	--oversampling_premises data/training/order_from_proof/train_standard.tgt.counts \
	--output_prefix $TRAIN_DATA/train_standard
```

## Training

We assume that:
* `TRAIN_DATA` is a path to directory with training data which we want use for
	training,
* `OPENNMT` is a path to OpenNMT,
* `NOTATION` is either `standard` or `prefix` -- type of notation we want to
	use as source for NMT model

Final preprocessing:
```
python3 $OPENNMT/preprocess.py \
	-train_src $TRAIN_DATA/train_$NOTATION.src \
	-train_tgt $TRAIN_DATA/train_$NOTATION.tgt \
	-tgt_seq_length 1000 -src_seq_length 1000 \
	-save_data $TRAIN_DATA/onmt_$NOTATION
```
Training:
```
MODEL_PATH=models/model_$NOTATION; mkdir models
python3 $OPENNMT/train.py \
	-data $TRAIN_DATA/onmt_$NOTATION \
	-world_size 1 -gpu_ranks 0 \
	-save_model $MODEL_PATH
```

## Producing predictions from a trained NMT model
```
mkdir data/predictions
python3 $OPENNMT/translate.py \
	-model models/$MODEL_PATH \
	-beam_size 10 -n_best 10 \
	-src data/testing/statements.$NOTATION	\
	-replace_unk -verbose -gpu 0 \
	-min_length 1 -max_length 64 \
	-output data/predictions/$MODEL_PATH.preds
```

## Evaluating predictions with similarity metrics
First we need to produce unions of predictions for each testing
theorems, which we will compare to the unions of dependencies from
know proofs.
```
python3 scripts/data_manipulation/predictions_to_dependencies.py \
	data/predictions/$MODEL_PATH.preds \
	data/testing/names \
	--only_unions \
	> data/predictions/$MODEL_PATH.preds.unions
```

Computing Jaccard index and Coverage between unions of predictions and unions
of dependencies:
```
python3 scripts/evaluation/jaccard_index.py \
	data/testing/dependencies.unions \
	data/predictions/$MODEL_PATH.preds.unions
```

## ATP evaluation
We will try to prove each theorem with 10 sets of proposed premises plus
the union of them. To prepare these dependencies run:
```
python3 scripts/data_manipulation/predictions_to_dependencies.py \
	data/predictions/$MODEL_PATH.preds \
	data/testing/names \
	> data/predictions/$MODEL_PATH.preds.deps
```
Running evaluation with E prover with prepared predicted dependencies:
```
mkdir atp_eval_proofs
python3 scripts/evaluation/atp_evaluation.py \
	$PREDS.deps \
	data/statements/standard_full \
	--dir_for_proofs data/atp_eval_proofs
```

## Results
Directory `results` contains predictions obtained from the NMT models trained
on various training data. There are also prediction from XGBoost.
`results/test_theorems` -- names of test theorems used in our experiments.
`results/test_theorems_initial_dependencies` -- dependencies extracted from
	the initial proofs from `data/proofs`.
For each NMT / XGBoost model there are 3 files:
- `*.deps.proved` -- predicted dependencies which led to a proof,
- `*.deps.not_proved` -- predicted dependencies which did not lead to a proof,
- `*.deps.proved.used` -- same as `*.deps.proved` but with additional information,
	which premises from the proposed where actually used in the proof.

