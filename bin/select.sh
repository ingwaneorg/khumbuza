#!/bin/bash

directory="/mnt/ssd/Applications/khumbuza"
database="tasks.db"

echo "========================================================================"

sqlite3 ${directory}/${database} <<EOF
SELECT *
FROM task
ORDER by id
EOF

echo "------------------------------------------------------------------------"

#EOF
