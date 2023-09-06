#!/bin/bash

SEED=727
SEED2=1

NODES=100
TASKS=50
USERS=10

POP_SIZE=100
N_GEN=100
MUTATION_PROB=0.2
ALGORITHM='NSGA3'

N_REF_POINTS=16
N_PARTITIONS=$((N_REF_POINTS+1))

# Generate $N_REF_POINTS Lambda values between [0,1]
LAMBDA_LIST=$(python3 -c "for i in range(1,$N_REF_POINTS+1): print(i/($N_REF_POINTS+1))")

i=1
for l in $LAMBDA_LIST; do
	echo "$i/$N_REF_POINTS"

	# Async call
	python3 main.py --seed $SEED2 solve \
		-i "data/network/ntw_"$SEED"_"$NODES":"$TASKS":"$USERS \
		--pop_size $POP_SIZE --n_gen $N_GEN --mutation_prob $MUTATION_PROB \
		--algorithm $ALGORITHM --n_partitions $N_PARTITIONS --single_mode --lmb $l \
		--print > "/tmp/ref_$i" &

	pids[${i}]=$!
	i=$((i+1))
done

for pid in ${pids[*]}; do
	wait $pid
done

# Save outputs
array=()
for i in $(seq 1 $N_REF_POINTS); do
	array+="$(cat "/tmp/ref_$i" | grep . | awk '{print "[" $1 "," $2 "]"}')"
done

echo "[${array[*]//][/],[}]" > "data/solutions/$NODES:$TASKS:$USERS/ref_points/rp_"$ALGORITHM"_"$SEED":"$SEED2"_2"

