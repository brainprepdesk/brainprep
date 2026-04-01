#!/bin/bash
set -e

# Welcome message
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
cat <<EOF
============================================================
 🧠  BrainPrep — Neuroimaging Preprocessing Tool
============================================================

  Version : 2
  License : CeCILL-B
  Source  : https://github.com/brainprepdesk/brainprep

  Container started at : $START_TIME

  This container provides a fully isolated environment.

  Run "brainprep --help" or any subcommand to get started.
============================================================
EOF

# First arguments are allowed patterns until we hit "--"
read -r -a DEFAULT_ARGS_ARRAY <<< "$DEFAULT_ARGS"
ALLOWED_WORKFLOWS=()
for pattern in "${DEFAULT_ARGS_ARRAY[@]}"; do
    ALLOWED_WORKFLOWS+=("brainprep $pattern")
done

# Remaining arguments are the actual user command
USER_CMD=("$@")

if [ ${#USER_CMD[@]} -lt 2 ]; then
    echo -e "Error: \e[31m✖\e[0m no valid command provided."
    echo "Usage: brainprep <workflow> <parameters>"
    exit 1
fi

CMD="${USER_CMD[0]}"
SUBCMD="${USER_CMD[1]}"

# Validate against allowed patterns
VALID=false
for pattern in "${ALLOWED_WORKFLOWS[@]}"; do
    read -r p1 p2 <<< "$pattern"
    if [[ "$CMD" == "$p1" && "$SUBCMD" == "$p2" ]]; then
        VALID=true
        break
    fi
done

if ! $VALID; then
    echo -e "Error: \e[31m✖\e[0m invalid workflow."
    echo "Allowed workflows:"
    for p in "${ALLOWED_WORKFLOWS[@]}"; do
        echo "  $p <parameters>"
    done
    exit 1
fi

# Execute the command
/opt/brainprep/.pixi/envs/default/bin/brainprep "${USER_CMD[@]:1}"
