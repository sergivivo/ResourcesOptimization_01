#!/bin/bash

SEED=722
SEED2=1

NODES=20
TASKS=20
USERS=20

POP_SIZE=100
N_GEN=100
MUTATION_PROB=0.2
ALGORITHM='ILP'

N_POINTS=5
N_PARTITIONS=$((N_POINTS+1))

LAMBDA_LIST='0.0 0.1 0.5 0.9 1.0'
#LAMBDA_LIST=$(python3 -c "for i in range(1,$N_REF_POINTS+1): print(i/($N_REF_POINTS+1))")

for NODES in $(seq 20 20 40); do
for TASKS in $(seq 20 20 $((NODES*2))); do
for USERS in $(seq 20 20 $NODES); do
	echo $NODES $TASKS $USERS

	mkdir -p "data/solutions/$NODES-$TASKS-$USERS/ref_points"
	mkdir -p "data/solutions/$NODES-$TASKS-$USERS/tmp"

	i=1
	for l in $LAMBDA_LIST; do
		echo "  $i/$N_POINTS: lambda=$l"

		# Async call
		python3 main.py --seed $SEED2 solve \
			-i "data/network/ntw_"$SEED"_"$NODES"-"$TASKS"-"$USERS \
			--pop_size $POP_SIZE --n_gen $N_GEN --mutation_prob $MUTATION_PROB \
			--algorithm $ALGORITHM --n_partitions $N_PARTITIONS --single_mode --lmb $l \
			--output "data/solutions/$NODES-$TASKS-$USERS/tmp/ref_$i" &

		pids[${i}]=$!
		i=$((i+1))
	done

	i=1
	for pid in ${pids[*]}; do
		wait $pid
		if [ $? -eq 0 ]; then
			array[${i}]="$(cat "data/solutions/$NODES-$TASKS-$USERS/tmp/ref_$i" | grep . | awk '{print "[" $1 "," $2 "]"}')"
		fi
		i=$((i+1))
	done

	echo "[${array[*]}]" | tr -s '[:blank:]' ',' > "data/solutions/$NODES-$TASKS-$USERS/ref_points/rp_"$ALGORITHM"_"$SEED"-"$SEED2"_omin0"

done
done
done

