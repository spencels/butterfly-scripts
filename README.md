# butterfly-scripts
Scripts, bits, and bots for administrating the Bots and Butterflies website.

## Setup

This repo relies on a few environmental pieces to work:

* Software: Ansible, Python 3, s3cmd
* Environment variables: `VULTR_API_KEY`
* Files: `~/buttsdev/vault-pass.txt` (Ansible vault password)
* Files (developent only): `~/buttsdev/inventory.yml`

Before running anything, use this command to set up your shell environment:

```
source env.sh
```

Or, when making changes to prod, run:

```
source env.sh prod
```