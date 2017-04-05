#! /bin/bash

function join_by { local d=$1; shift; echo -n "$1"; shift; printf "%s" "${@/#/$d}"; }

matlab -nojvm -r "process_spk_files({'$(join_by \',\' $@)'}); exit"
