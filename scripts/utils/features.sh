input=$1
output=$2
#formulas_type=$3
tmp_file=tmp/aaa
#swipl -nodebug -A0 -L0 -G0 -T0  -g "[utils/features],declare_TPTP_operators1,[$all_problems],time(($formulas_type(A,B,C),bag_of_walks_top(C,Res,P),write(A),write(P),nl,fail)),halt." > $tmp_file
swipl -A0 -L0 -G0 -T0  -g "[scripts/utils/features],declare_TPTP_operators1,[$input],time((fof(A,B,C),bag_of_walks_top(C,Res,P),write(A),write(P),nl,fail)),halt." > $tmp_file
sort -u $tmp_file > $output
sed -i 's/\[/:/g' $output
sed -i 's/\]//g' $output
sed -i 's/,/ /g' $output
sed -i 's/\-/:/g' $output

