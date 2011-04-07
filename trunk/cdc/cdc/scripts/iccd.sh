#!/bin/bash
echo  "Initializing... "
#iinput_file="$1"
echo "*$1*"
mkdir "$1"
#output_file=$2
echo  "Directory  "$1 "was created" 
#echo  "output"$2
cp $1.v ./$1
cd ./$1
./../new_cdc.py $1.v >  $1_cdc_paths.txt # the output is in new.v
./../insert_mux_p1 new.v tmp_out1.txt tmp_out2.txt inout.name # inout.name is used to generate toptester.v
./../insert_mux_p2 tmp_out1.txt tmp_out2.txt $1_mux_inserted.v #$1_changed.v is used by modelsim

# select sender dff and recv dff from cdc_path.txt
python sel_recv_dff.py $1_cdc_paths.txt bit_clk_pad_i, clk_i
# generate do files and f2 files
python gen_do.py

# given the .v file, output test bench for modelsim
python gen_ms.py $1_mux_inserted.v

#for (( i=0; i<=$2; i++))  # it is fault number
#do
#cd ..
#./myfile.run


./../extract_pi_ffs $$.pattern msr1_$$.pattern # num.pattern is generated by zhiqiu file as an output of fastscan and msr1_num.pattern is used by modelsim as the input value

#done
#rm tmp_out1.txt
#rm tmp_out2.txt
echo "[done]"
