#!/bin/bash
# Usage: run-mysqldump.sh username password outputfile
mysqldump --user="$1" --password="$2" --all_databases | gzip >"$3"
exit $?