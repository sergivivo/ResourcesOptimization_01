#!/bin/bash

SEED=727

NODES=100
TASKS=50
USERS=10

POP_SIZE=100
N_GEN=100
MUTATION_PROB=0.2
ALGORITHM='RNSGA2'
N_PARTITIONS=16

#python3 main.py --seed $SEED generate -p 0.15 \
#	--n_nodes $NODES --n_tasks $TASKS --n_users $USERS \
#	-o "data/network/ntw_"$SEED"_"$NODES"_"$TASKS"_"$USERS

#for ALGORITHM in 'RNSGA2'; do
#	for SEED2 in 5; do
#		python3 main.py --seed $SEED2 solve \
#			-i "data/network/ntw_"$SEED"_"$NODES"_"$TASKS"_"$USERS \
#			--pop_size $POP_SIZE --n_gen $N_GEN --mutation_prob $MUTATION_PROB -v --save_history \
#			--algorithm $ALGORITHM \
#			-o "data/solutions/"$ALGORITHM"_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN
#	done
#done

# TODO: Monitorizar el tiempo de ejecución, para tener métricas más rigurosas para hacer un estudio

#for ALGORITHM in 'NSGA2' 'NSGA3' 'UNSGA3' 'CTAEA' 'SMSEMOA' 'RVEA'; do
#	for SEED2 in {1..5}; do
#		python3 main.py --seed $SEED plot \
#			-i "data/solutions/"$ALGORITHM"_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN \
#			--history \
#			--title "Objective space - Convergence ($ALGORITHM)" \
#			--x_label "Mean latency between users/services" \
#			--y_label "Occupied nodes"
#	done
#done

for SEED2 in {1..5}; do
	python3 main.py --seed $SEED plot \
		-i "data/solutions/NSGA2_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN \
		   "data/solutions/NSGA3_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN \
		   "data/solutions/UNSGA3_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN \
		   "data/solutions/CTAEA_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN \
		   "data/solutions/SMSEMOA_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN \
		   "data/solutions/RVEA_"$SEED":"$SEED2"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN \
		--comparison \
		--legend NSGA2 \
			 NSGA3 \
			 UNSGA3 \
			 CTAEA \
			 SMSEMOA \
			 RVEA \
		--title "Objective space - Comparison between algorithms" \
		--x_label "Mean latency between users/services" \
		--y_label "Occupied nodes"
done



