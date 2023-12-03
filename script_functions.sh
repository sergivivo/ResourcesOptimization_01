#!/bin/bash

# ==============================================================================
# FUNCTIONS
# ==============================================================================
zeropad_left() {
	printf "%0$2d\n" $1
}

get_network_filename() {
	local SEED=$(zeropad_left $1 3)
	local NODES=$(zeropad_left $2 3)
	local TASKS=$(zeropad_left $3 3)
	local USERS=$(zeropad_left $4 3)
	local COMMUNITIES=$5

	if [ $COMMUNITIES = true ]; then
		local SUFFIX="C"
	else
		local SUFFIX="H"
	fi

	echo "ntw_"$SEED"_"$NODES"-"$TASKS"-"$USERS"_"$SUFFIX
}

generate() {
	mkdir -p "$NTW_PREFIX"

	if [ $COMMUNITIES = true ]; then
		local C_OPT=--communities
	else
		local C_OPT=
	fi

	NTW_FILENAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"

	python3 main.py --seed $SEED generate \
		--n_nodes $NODES --n_tasks $TASKS --n_users $USERS \
		$C_OPT -o "$NTW_PREFIX/$NTW_FILENAME"
}

get_solution_path() {
	local NTW_NAME=$1
	local N_REPLICAS=$(zeropad_left $2 3)
	local ALGORITHM=$3

	if [ $ALGORITHM = "ILP" ]; then
		local ALG_TYPE="ILP"
	else
		local ALG_TYPE="Genetics"
	fi

	echo "$NTW_NAME/Replicas$N_REPLICAS/$ALG_TYPE"
}

get_solution_filename() {
	local ALGORITHM=$1
	local SEED=$2
	local POP_SIZE=$(zeropad_left $3 3)
	local N_GEN=$(zeropad_left $4 3)
	local SV=$5
	local CV=$6
	local MV=$7
	local MM=$8
	local MC=$9

	echo $ALGORITHM"_"$SEED"_"$POP_SIZE"-"$N_GEN"_SV"$SV"-CV"$CV"-MV"$MV"_MM"$MM"-MC"$MC".txt"
}

solve() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"
	SOL_NAME="$(get_solution_filename $ALGORITHM $SEED2 $POP_SIZE $N_GEN $SAMPLING_VERSION $CROSSOVER_VERSION $MUTATION_VERSION $MUTATION_PROB_MOVE $MUTATION_PROB_CHANGE)"

	mkdir -p "$SOL_PREFIX/$SOL_PATH" 

	python3 main.py --seed $SEED2 solve \
		-i "$NTW_PREFIX/$NTW_NAME" \
		--objectives ${OBJECTIVES[*]} \
		--pop_size $POP_SIZE --n_gen $N_GEN \
		--n_replicas $N_REPLICAS \
		--n_partitions $N_PARTITIONS \
		--sampling_version $SAMPLING_VERSION \
		--crossover_version $CROSSOVER_VERSION \
		--mutation_version $MUTATION_VERSION \
		--mutation_prob_move $MUTATION_PROB_MOVE \
		--mutation_prob_change $MUTATION_PROB_CHANGE \
		--save_history \
		--algorithm $ALGORITHM \
		-o "$SOL_PREFIX/$SOL_PATH/$SOL_NAME"

}

arrange() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"

	ALG_FILES=()
	for SEED2 in $(seq 1 1 $N_EXECUTIONS); do
		SOL_NAME="$(get_solution_filename $ALGORITHM $SEED2 $POP_SIZE $N_GEN $SAMPLING_VERSION $CROSSOVER_VERSION $MUTATION_VERSION $MUTATION_PROB_MOVE $MUTATION_PROB_CHANGE)"
		ALG_FILES[${SEED2}]="$SOL_PREFIX/$SOL_PATH/$SOL_NAME"
	done

	SOL_NAME="$(get_solution_filename $ALGORITHM "A" $POP_SIZE $N_GEN $SAMPLING_VERSION $CROSSOVER_VERSION $MUTATION_VERSION $MUTATION_PROB_MOVE $MUTATION_PROB_CHANGE)"
	python3 main.py arrange \
		--n_objectives $N_OBJECTIVES \
		-i ${ALG_FILES[*]} \
		-o "$SOL_PREFIX/$SOL_PATH/$SOL_NAME"

}

get_ref_points() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"

	rm -rf "$SOL_PREFIX/$SOL_PATH/ref_points"
	rm -rf "$SOL_PREFIX/$SOL_PATH/tmp"
	rm -rf "$SOL_PREFIX/$SOL_PATH/log"

	mkdir -p "$SOL_PREFIX/$SOL_PATH/ref_points"
	mkdir -p "$SOL_PREFIX/$SOL_PATH/tmp"
	mkdir -p "$SOL_PREFIX/$SOL_PATH/log"

	i=1
	for l in $LAMBDA_LIST; do
		# Async call
		{ time python3 main.py --seed $SEED2 solve \
			-i "$NTW_PREFIX/$NTW_NAME" \
			--algorithm "ILP" --n_partitions $N_PARTITIONS --single_mode --lmb $l \
			--n_replicas $N_REPLICAS \
			--verbose \
			--output "$SOL_PREFIX/$SOL_PATH/tmp/ref_$i"
		} &> "$SOL_PREFIX/$SOL_PATH/log/log_$i" &
		pids[${i}]=$!
		i=$((i+1))
	done

	i=1
	for pid in ${pids[*]}; do
		wait $pid
		if [ $? -eq 0 ]; then
			array[${i}]="$(cat "$SOL_PREFIX/$SOL_PATH/tmp/ref_$i" | grep . | awk '{print "[" $1 "," $2 "]"}')"
		fi
		i=$((i+1))
	done

	echo "[${array[*]}]" | tr -s '[:blank:]' ',' > "$SOL_PREFIX/$SOL_PATH/ref_points/rp_$ALGORITHM"
}

get_ref_points_seq() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"

	rm -rf "$SOL_PREFIX/$SOL_PATH/ref_points"
	rm -rf "$SOL_PREFIX/$SOL_PATH/tmp"
	rm -rf "$SOL_PREFIX/$SOL_PATH/log"

	mkdir -p "$SOL_PREFIX/$SOL_PATH/ref_points"
	mkdir -p "$SOL_PREFIX/$SOL_PATH/tmp"
	mkdir -p "$SOL_PREFIX/$SOL_PATH/log"

	i=1
	for l in $LAMBDA_LIST; do
		# Async call
		{ time python3 main.py --seed $SEED2 solve \
			-i "$NTW_PREFIX/$NTW_NAME" \
			--algorithm "ILP" --n_partitions $N_PARTITIONS --single_mode --lmb $l \
			--n_replicas $N_REPLICAS \
			--verbose \
			--output "$SOL_PREFIX/$SOL_PATH/tmp/ref_$i"
		} &> "$SOL_PREFIX/$SOL_PATH/log/log_$i"

		array[${i}]="$(cat "$SOL_PREFIX/$SOL_PATH/tmp/ref_$i" | grep . | awk '{print "[" $1 "," $2 "]"}')"
		i=$((i+1))
	done

	echo "[${array[*]}]" | tr -s '[:blank:]' ',' > "$SOL_PREFIX/$SOL_PATH/ref_points/rp_$ALGORITHM"
}

plot_convergence() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"
	SOL_NAME="$(get_solution_filename $ALGORITHM $SEED2 $POP_SIZE $N_GEN $SAMPLING_VERSION $CROSSOVER_VERSION $MUTATION_VERSION $MUTATION_PROB_MOVE $MUTATION_PROB_CHANGE)"

	python3 main.py --seed $SEED plot \
		--n_objectives $N_OBJECTIVES \
		-i "$SOL_PREFIX/$SOL_PATH/$SOL_NAME" \
		--history \
		--title "Objective space - Convergence ($ALGORITHM) - $NODES:$TASKS:$USERS" \
		--x_label "Mean latency between users/services" \
		--y_label "Occupied nodes" \
		--trim_gen
}

get_algorithm_files() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"

	ALG_FILES=()
	i=0
	for ALG in ${ALGORITHMS[*]}; do
		SOL_NAME="$(get_solution_filename $ALG $SEED2 $POP_SIZE $N_GEN $SAMPLING_VERSION $CROSSOVER_VERSION $MUTATION_VERSION $MUTATION_PROB_MOVE $MUTATION_PROB_CHANGE)"
		ALG_FILES[${i}]="$SOL_PREFIX/$SOL_PATH/$SOL_NAME" 
		i=$((i+1))
	done
	echo ${ALG_FILES[*]}
}

get_operator_version_files() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"

	OP_FILES=()
	i=0
	for SV in ${SAMPLING_VERSION_LIST[*]}; do
	for CV in ${CROSSOVER_VERSION_LIST[*]}; do
	for MV in ${MUTATION_VERSION_LIST[*]}; do
		SOL_NAME="$(get_solution_filename $ALGORITHM $SEED2 $POP_SIZE $N_GEN $SV $CV $MV $MUTATION_PROB_MOVE $MUTATION_PROB_CHANGE)"
		OP_FILES[${i}]="$SOL_PREFIX/$SOL_PATH/$SOL_NAME"
		i=$((i+1))
	done
	done
	done

	echo ${OP_FILES[*]}
}

get_operator_version_legend() {
	OP_LEGEND=()
	i=0
	for SV in ${SAMPLING_VERSION_LIST[*]}; do
	for CV in ${CROSSOVER_VERSION_LIST[*]}; do
	for MV in ${MUTATION_VERSION_LIST[*]}; do
		OP_LEGEND[${i}]="SV$SV:CV$CV:MV$MV"
		i=$((i+1))
	done
	done
	done

	echo ${OP_LEGEND[*]}
}

get_mutation_files() {
	NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS $ALGORITHM)"

	MUT_FILES=()
	i=0
	for MM in ${MUTATION_PROB_MOVE_LIST[*]}; do
	for MC in ${MUTATION_PROB_CHANGE_LIST[*]}; do
		SOL_NAME="$(get_solution_filename $ALGORITHM $SEED2 $POP_SIZE $N_GEN $SAMPLING_VERSION $CROSSOVER_VERSION $MUTATION_VERSION $MM $MC)"
		MUT_FILES[${i}]="$SOL_PREFIX/$SOL_PATH/$SOL_NAME"
		i=$((i+1))
	done
	done

	echo ${MUT_FILES[*]}
}

get_mutation_legend() {
	MUT_LEGEND=()
	i=0
	for MM in ${MUTATION_PROB_MOVE_LIST[*]}; do
	for MC in ${MUTATION_PROB_CHANGE_LIST[*]}; do
		MUT_LEGEND[${i}]="MM$MM:MC$MC"
		i=$((i+1))
	done
	done

	echo ${MUT_LEGEND[*]}
}

plot_comparison() {
	local VAR1=$1
	local INPUT="${VAR1:=algorithms}"
	local VAR2=$2
	local SUFFIX="${VAR2:=}"
	if [ $INPUT = "algorithms" ]; then
		FILES=$(get_algorithm_files)
		FILE_LEGEND=${ALGORITHMS[*]}
		TITLE="algorithms"
	elif [ $INPUT = "operator_versions" ]; then
		FILES=$(get_operator_version_files)
		FILE_LEGEND=$(get_operator_version_legend)
		TITLE="operator versions"
	elif [ $INPUT = "mutations" ]; then
		FILES=$(get_mutation_files)
		FILE_LEGEND=$(get_mutation_legend)
		TITLE="mutations"
	fi

	local NTW_NAME="$(get_network_filename $SEED $NODES $TASKS $USERS $COMMUNITIES)"
	local SOL_PATH="$(get_solution_path $NTW_NAME $N_REPLICAS 'ILP')"
	local ILP_FILE="$SOL_PREFIX/$SOL_PATH/ref_points/rp_ILP"
	if [ -f "$ILP_FILE" ]; then
		local REF_POINTS_OPT=(--ref_points $(cat "$ILP_FILE"))
	else
		local REF_POINTS_OPT=()
	fi
	
	python3 main.py --seed $SEED plot \
		--n_objectives $N_OBJECTIVES \
		${REF_POINTS_OPT[*]} -i $FILES \
		--comparison \
		--legend $FILE_LEGEND \
		--title "Objective space - Comparison between $TITLE $SUFFIX - $NODES:$TASKS:$USERS" \
		--x_label "Mean latency between users/services" \
		--y_label "Occupied nodes" \
		--z_label "Mean hops to service" 
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



