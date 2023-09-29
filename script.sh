#!/bin/bash

SEED=722

NODES=40
TASKS=80
USERS=20

mkdir -p "data/network"

#echo "NETWORK GENERATION"
#for NODES in $(seq 20 20 40); do
#for TASKS in $(seq 20 20 $((NODES*2))); do
#for USERS in $(seq 20 20 $NODES); do
#	echo "  $NODES:$TASKS:$USERS"
#	python3 main.py --seed $SEED generate \
#		--n_nodes $NODES --n_tasks $TASKS --n_users $USERS \
#		-o "data/network/ntw_"$SEED"_"$NODES"-"$TASKS"-"$USERS
#done
#done
#done
#echo "DONE"


POP_SIZE=100
N_GEN=100
MUTATION_PROB=0.2
ALGORITHM='RNSGA2'
N_PARTITIONS=16

mkdir -p "data/solutions/$NODES-$TASKS-$USERS"
mkdir -p "data/plot/$NODES-$TASKS-$USERS"

#echo "PROBLEM SOLVING"
#for NODES in $(seq 20 20 40); do
#for TASKS in $(seq 20 20 $((NODES*2))); do
#for USERS in $(seq 20 20 $NODES); do
#echo "  $NODES:$TASKS:$USERS"
#
#for ALGORITHM in 'NSGA2' 'NSGA3' 'UNSGA3' 'CTAEA' 'SMSEMOA' 'RVEA'; do
#	echo "    $ALGORITHM"
#	for SEED2 in {1..5}; do
#		echo "      Execution $SEED2"
#		python3 main.py --seed $SEED2 solve \
#			-i "data/network/ntw_"$SEED"_"$NODES"-"$TASKS"-"$USERS \
#			--pop_size $POP_SIZE --n_gen $N_GEN --mutation_prob $MUTATION_PROB --save_history \
#			--algorithm $ALGORITHM \
#			-o "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN &
#
#		pids[${SEED2}]=$!
#	done
#
#	for pid in ${pids[*]}; do
#		wait $pid
#	done
#
#	python3 main.py arrange \
#		-i "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-1_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
#		   "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-2_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
#		   "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-3_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
#		   "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-4_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
#		   "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-5_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
#		-o "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN
#	echo "    DONE"
#done
#
#done
#done
#done

# TODO: Monitorizar el tiempo de ejecución, para tener métricas más rigurosas para hacer un estudio

#for NODES in $(seq 20 20 40); do
#for TASKS in $(seq 20 20 $((NODES*2))); do
#for USERS in $(seq 20 20 $NODES); do
#
#for ALGORITHM in 'NSGA2' 'NSGA3' 'UNSGA3' 'CTAEA' 'SMSEMOA' 'RVEA'; do
#	for SEED2 in {1..1}; do
#		python3 main.py --seed $SEED plot \
#			-i "data/solutions/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
#			--history \
#			--title "Objective space - Convergence ($ALGORITHM) - $NODES:$TASKS:$USERS" \
#			--x_label "Mean latency between users/services" \
#			--y_label "Occupied nodes"
#	done
#done
#
#done
#done
#done

for NODES in $(seq 20 20 40); do
for TASKS in $(seq 20 20 $((NODES*2))); do
for USERS in $(seq 20 20 $NODES); do

python3 main.py --seed $SEED plot \
	-i "data/solutions/$NODES-$TASKS-$USERS/NSGA2_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
	   "data/solutions/$NODES-$TASKS-$USERS/NSGA3_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
	   "data/solutions/$NODES-$TASKS-$USERS/UNSGA3_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
	   "data/solutions/$NODES-$TASKS-$USERS/CTAEA_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
	   "data/solutions/$NODES-$TASKS-$USERS/SMSEMOA_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
	   "data/solutions/$NODES-$TASKS-$USERS/RVEA_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
	--ref_points $(cat "data/solutions/$NODES-$TASKS-$USERS/ref_points/rp_ILP_"$SEED"-1") \
	--comparison \
	--legend NSGA2 \
		 NSGA3 \
		 UNSGA3 \
		 CTAEA \
		 SMSEMOA \
		 RVEA \
	--title "Objective space - Comparison between algorithms - $NODES:$TASKS:$USERS" \
	--x_label "Mean latency between users/services" \
	--y_label "Occupied nodes"

done
done
done



