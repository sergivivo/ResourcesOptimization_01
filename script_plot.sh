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

### Looping seeds + thread handling
#for SEED2 in $(seq 1 1 $N_EXECUTIONS); do
#	:
#	pids[${SEED2}]=$!
#done
#
#for pid in ${pids[*]}; do
#	wait $pid
#done

SEED2=A
plot_comparison operator_versions "for $ALGORITHM"

#SAMPLING_VERSION=0
#CROSSOVER_VERSION=2
#plot_comparison algorithms "for SV$SAMPLING_VERSION:CV$CROSSOVER_VERSION"
