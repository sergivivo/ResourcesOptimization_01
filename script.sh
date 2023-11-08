#!/bin/bash

# ==============================================================================
# CONSTANTS
# ==============================================================================
SEED=722

NODES=20
TASKS=40
USERS=20

N_REPLICAS=4
MUTATION_PROB_MOVE=0.1
MUTATION_PROB_CHANGE=0.1

POP_SIZE=500
N_GEN=200
ALGORITHM='NSGA2'
ALGORITHMS=('NSGA2' 'NSGA3' 'UNSGA3' 'CTAEA' 'SMSEMOA' 'RVEA')
N_PARTITIONS=16

OBJECTIVES=('distance' 'nodes')
N_OBJECTIVES=2

N_EXECUTIONS=4
SEED2=1

PREFIX="data/solutions/P$POP_SIZE-G$N_GEN/R1-MM$MUTATION_PROB_MOVE/communities"
PREFIX2="data/solutions/P$POP_SIZE-G$N_GEN/R1-MM$MUTATION_PROB_MOVE"

# ==============================================================================
# FUNCTIONS
# ==============================================================================
generate() {
	mkdir -p "data/network"
	python3 main.py --seed $SEED generate \
		--n_nodes $NODES --n_tasks $TASKS --n_users $USERS \
		--communities \
		-o "data/network/ntw_"$SEED"_"$NODES"-"$TASKS"-"$USERS
}

solve() {
	mkdir -p "$PREFIX/$NODES-$TASKS-$USERS"

	python3 main.py --seed $SEED2 solve \
		-i "data/network/ntw_"$SEED"_"$NODES"-"$TASKS"-"$USERS \
		--objectives ${OBJECTIVES[*]} \
		--pop_size $POP_SIZE --n_gen $N_GEN \
		--n_replicas $N_REPLICAS \
		--mutation_prob_move $MUTATION_PROB_MOVE \
		--mutation_prob_change $MUTATION_PROB_CHANGE \
		--save_history \
		--algorithm $ALGORITHM \
		-o "$PREFIX/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN

}

arrange() {
	ALG_FILES=()
	for SEED2 in $(seq 1 1 $N_EXECUTIONS); do
		ALG_FILES[${SEED2}]="$PREFIX/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN
	done

	python3 main.py arrange \
		--n_objectives $N_OBJECTIVES \
		-i ${ALG_FILES[*]} \
		-o "$PREFIX/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-A_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN

}

plot_convergence() {
	python3 main.py --seed $SEED plot \
		--n_objectives $N_OBJECTIVES \
		-i "$PREFIX/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
		--history \
		--title "Objective space - Convergence ($ALGORITHM) - $NODES:$TASKS:$USERS" \
		--x_label "Mean latency between users/services" \
		--y_label "Occupied nodes" \
		--trim_gen
}

plot_comparison() {
	ALG_FILES=()
	i=0
	for ALGORITHM in ${ALGORITHMS[*]}; do
		ALG_FILES[${i}]="$PREFIX/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN
		i=$((i+1))
	done

	python3 main.py --seed $SEED plot \
		--n_objectives $N_OBJECTIVES \
		-i ${ALG_FILES[*]} \
		--comparison \
		--legend ${ALGORITHMS[*]} \
		--title "Objective space - Comparison between algorithms - $NODES:$TASKS:$USERS" \
		--x_label "Mean latency between users/services" \
		--y_label "Occupied nodes" \
		--z_label "Mean hops to service" 
		#--ref_points $(cat "$PREFIX/$NODES-$TASKS-$USERS/ref_points/rp_ILP_"$SEED"-1") \
}

send_telegram_message() {

	# Send message using Telegram Bot API to notify that the process has finished
	ME=$(basename "$0")
	TOKEN=$(cat ../token.txt)
	CHAT_ID=$(cat ../chat_id.txt)
	HOSTNAME=$(hostname)
	curl -X POST -H 'Content-Type: application/json' \
		-d '{"chat_id": '$CHAT_ID', "text": "Script '$ME' has finished executing on server '$HOSTNAME'"}' \
		"https://api.telegram.org/bot$TOKEN/sendMessage"
	echo

}

# ==============================================================================
# PROGRAM
# ==============================================================================

### Network
# generate

### Problem solving
# solve
# arrange

### Plotting
# plot_comparison
# plot_convergence

### Helpers
# send_telegram_message

### Looping networks
#for NODES in $(seq 20 20 20); do
#for TASKS in $(seq 20 20 $((NODES*2))); do
#for USERS in $(seq 20 20 $NODES); do
#	:
#done
#done
#done

### Looping algorithms
#for ALGORITHM in ${ALGORITHMS[*]}; do
#	:
#done

### Looping seeds + thread handling
#for SEED2 in $(seq 1 1 $N_EXECUTIONS); do
#	:
#	pids[${SEED2}]=$!
#done
#
#for pid in ${pids[*]}; do
#	wait $pid
#done


for NODES in $(seq 20 20 40); do
for TASKS in $(seq 20 20 $((NODES*2))); do
for USERS in $(seq 20 20 $NODES); do
	for ALGORITHM in ${ALGORITHMS[*]}; do
		python3 main.py --seed $SEED plot \
			--n_objectives $N_OBJECTIVES \
			-i "$PREFIX/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
			   "$PREFIX2/$NODES-$TASKS-$USERS/"$ALGORITHM"_"$SEED"-"$SEED2"_"$NODES"-"$TASKS"-"$USERS"_"$POP_SIZE"-"$N_GEN \
			--comparison \
			--legend "$ALGORITHM communities" \
			         "$ALGORITHM without communities" \
			--title "Objective space - Comparison between algorithms - $NODES:$TASKS:$USERS" \
			--x_label "Mean latency between users/services" \
			--y_label "Occupied nodes" \
			--z_label "Mean hops to service" 
	done

done
done
done

