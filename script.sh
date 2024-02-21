#!/bin/bash

source script_constants.sh
source script_functions.sh

# ==============================================================================
# PROGRAM
# ==============================================================================

### Network
# generate $SEED $NODES $TASKS $USERS $COMMUNITIES

### Problem solving
# solve
# arrange

### Plotting
# plot_comparison
# plot_convergence

### Helpers
# send_telegram_message

### Looping networks
#for NODES in $(seq 20 20 40); do
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

### Looping operator versions
#for SAMPLING_VERSION in ${SAMPLING_VERSION_LIST[*]}; do
#for CROSSOVER_VERSION in ${CROSSOVER_VERSION_LIST[*]}; do
#for MUTATION_VERSION in ${MUTATION_VERSION_LIST[*]}; do
#	:
#done
#done
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

#TODO: https://scikit-learn.org/stable/auto_examples/linear_model/plot_polynomial_interpolation.html

NODES=50
TASKS=50
USERS=25

#for POP_SIZE in ${POP_SIZES[*]}; do
#	echo "  POP_SIZE = $POP_SIZE"
for ALGORITHM in ${ALGORITHMS[*]}; do
	#echo "  ALGORITHM = $ALGORITHM"
	#N_ITER=$((
	#		N_EXECUTIONS % N_PROC == 0 ?
	#		N_EXECUTIONS / N_PROC :
	#		N_EXECUTIONS / N_PROC + 1
	#	))
	#for ITER in $(seq 1 1 $N_ITER); do
	#	START=$(((ITER - 1) * N_PROC + 1))
	#	END=$((
	#			N_EXECUTIONS <= ITER * N_PROC ?
	#			N_EXECUTIONS :
	#			ITER * N_PROC
	#		))

	#	for SEED2 in $(seq $START 1 $END); do
	#		echo "    $SEED2"
	#		get_table population &
	#		pids[${SEED2}]=$!
	#	done

	#	for pid in ${pids[*]}; do
	#		wait $pid
	#	done

	#done

	get_table_group population

done


#generate
#
#for POP_SIZE in $(seq 50 50 300); do
#	echo "POP_SIZE = $POP_SIZE"
#
#	for ALGORITHM in ${ALGORITHMS[*]}; do
#		echo "  $ALGORITHM"
#
#		# Iterations needed for distributing N_EXECUTIONS 
#		# among N_PROC (max CPU usage control)
#		N_ITER=$((
#				N_EXECUTIONS % N_PROC == 0 ?
#				N_EXECUTIONS / N_PROC :
#				N_EXECUTIONS / N_PROC + 1
#			))
#		for ITER in $(seq 1 1 $N_ITER); do
#			START=$(((ITER - 1) * N_PROC + 1))
#			END=$((
#					N_EXECUTIONS <= ITER * N_PROC ?
#					N_EXECUTIONS :
#					ITER * N_PROC
#				))
#
#			for SEED2 in $(seq $START 1 $END); do
#				echo "    $SEED2"
#				solve &
#				pids[${SEED2}]=$!
#			done
#
#			for pid in ${pids[*]}; do
#				wait $pid
#			done
#
#		done
#
#		arrange
#
#	done
#done

#arrange_all
#solution_to_ref_points 0.9
