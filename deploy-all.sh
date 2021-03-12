#!/bin/bash
if [[ -z "$ANSIBLE_CONFIG" ]]; then
  echo "No ANSIBLE_CONFIG found; source env.sh first."
  exit 1
fi

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ansible-playbook "$script_dir/ansible/all.yml" "$@"
exit $?