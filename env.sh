# Usage:
#   source ./env.sh  # dev config

function main() {
  local env="${1:-dev}"
  # Set vars.
  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  export ANSIBLE_CONFIG="$script_dir/ansible/ansible.cfg"
  echo "ANSIBLE_CONFIG=$ANSIBLE_CONFIG"
}
main "$@"
unset -f main