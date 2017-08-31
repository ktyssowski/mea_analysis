#! /bin/bash
function join_by { local d=$1; shift; echo -n "$1"; shift; printf "%s" "${@/#/$d}"; }

module load matlab/2017a
matlab -nodesktop -r "process_spk_files_parallel({'$(join_by \',\' $@)'}); exit"

