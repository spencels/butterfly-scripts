#!/usr/bin/env python3
"""Starts dev server."""
import vultr
import subprocess
import logging
import sys
import time
import subprocess
import pathlib
import json

import common

scripts_dir = pathlib.Path(__file__).parent.absolute()


def main():
  common.configure_logging()

  # Delete previous instance.
  common.stop_dev_server()

  # Get ID of the latest backup.
  logging.info('Getting latest backup ID...')
  backups = vultr.get_backups()
  viable_backups = (x for x in backups
                    if common.SERVER_LABEL in x['description']
                        and x['status'] == 'complete')
  latest = sorted(viable_backups, key=lambda x: x['date_created'], reverse=True)[0]
  backup_id = latest['id']
  logging.info(f'Found backup {backup_id} made on {latest["date_created"]}.')

  # Create the new instance.
  logging.info(f'Creating new {common.DEV_SERVER_NAME} instance...')
  instance = vultr.create_instance(
      region='lax', plan='vc2-1c-1gb', snapshot_id=backup_id,
      firewall_group_id=common.DEV_FIREWALL_GROUP, label=common.DEV_SERVER_NAME)
  logging.info(f'Created new {common.DEV_SERVER_NAME} instance.')
  dev_instance_id = instance['id']

  # Wait for the instance to be up.
  logging.info(f'Waiting for server to be operational...')
  while True:
    time.sleep(5)
    instance = vultr.get_instance(dev_instance_id)
    if instance['server_status'] in ['none', 'locked']:
      print('.', end='', flush=True)
      continue
    if instance['server_status'] != 'ok':
      logging.error(f'Detected bad server status "{instance["server_status"]}".')
      sys.exit(1)
    break
  logging.info(f'Server is ready at {instance["main_ip"]}.')

  # Run finalization playbook.
  playbook_vars = {'host_ip': instance["main_ip"], 'hostname': common.DEV_SERVER_NAME}
  subprocess.run(
    ['ansible-playbook',
     f'{scripts_dir}/dev-server-setup.yml',
     '-i', instance["main_ip"] + ',',
     '-u', common.ANSIBLE_USER,
     '-e', json.dumps(playbook_vars)],
    check=True) 
  logging.info('All done.')


if __name__ == '__main__':
  main()