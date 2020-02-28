in_dir=$1
out_dir=$2
N=$3
t=$4

mkdir $out_dir

process_one_proof(){
	out_file=$out_dir/`basename $1`
	python3 scripts/permut_from_tree/limited_permutations_1.py $1 $N $t > $out_file
}

for f in $in_dir/*
do
	P=3000
	((i=i%P)); ((i++==0)) && wait
	process_one_proof $f &
done
