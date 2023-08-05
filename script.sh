#!/bin/bash

SEED=727

NODES=50
TASKS=100
USERS=15

python3 main.py --seed $SEED generate -p 0.15 \
	--n_nodes $NODES --n_tasks $TASKS --n_users $USERS \
	-o "data/network/ntw_"$SEED"_"$NODES"_"$TASKS"_"$USERS

POP_SIZE=100
N_GEN=100
MUTATION_PROB=0.2

python3 main.py --seed $SEED solve \
	-i "data/network/ntw_"$SEED"_"$NODES"_"$TASKS"_"$USERS \
	--pop_size $POP_SIZE --n_gen $N_GEN --mutation_prob $MUTATION_PROB -v --save_history \
	-o "data/solutions/NSGA2_"$SEED"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN

python3 main.py --seed $SEED plot \
	-i "data/solutions/NSGA2_"$SEED"_"$NODES"_"$TASKS"_"$USERS"_"$N_GEN
