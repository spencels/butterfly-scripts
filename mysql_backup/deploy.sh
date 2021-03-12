#!/bin/bash

# cd to the directory of this file.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Flags
host=

function parse-args {
  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      -h|--host)
        host="$2"
        if [[ -z "$host" ]]; then
          echo "Must provide a host name."
          exit 1
        fi
        shift 2
        ;;
      *)
        echo "Error: Unexpected argument '$1'."
        exit 1
        shift
        ;;
    esac
  done

  if [[ -z "$host" ]]; then
    echo "Must provide a --host."
    exit 1
  fi
}

function main {
  if [[ -z "$ANSIBLE_CONFIG" ]]; then
    echo "Run \"source env.sh\" first."
    exit 1
  fi

  parse-args "$@"

  # Copy files over.
  ansible-playbook "$script_dir/deploy.yml" -e "hostname=$host mysql_backup_src=$script_dir"
}
main "$@"