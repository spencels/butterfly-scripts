# Usage:
#   source ./env.sh  # dev config

function main() {
  local env="$1"
  # Set vars.
  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  case $env in
  prod)
    # Clear so the ansible.cfg one is used.
    export ANSIBLE_INVENTORY="$script_dir/ansible/inventory.yml"
    ;;
  *)
    export ANSIBLE_INVENTORY="$HOME/buttsdev/inventory.yml"
    ;;
  esac
  echo "ANSIBLE_INVENTORY=$ANSIBLE_INVENTORY"

  export ANSIBLE_CONFIG="$script_dir/ansible/ansible.cfg"
  echo "ANSIBLE_CONFIG=$ANSIBLE_CONFIG"
}
main "$@"
unset -f main