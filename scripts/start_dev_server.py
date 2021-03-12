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

SERVER_LABEL = 'adhdbutts-wp'
DEV_SERVER_NAME = 'butts-dev2'
DEV_FIREWALL_GROUP = 'ba498c9a-106c-41b2-881a-144795427b90'
ANSIBLE_USER = 'spencels'
scripts_dir = pathlib.Path(__file__).parent.absolute()


def main():
  formatter = logging.Formatter(
      '%(levelname)-1.1s %(asctime)s: %(message)s',
      '%H:%M:%S')
  root_logger = logging.getLogger()
  root_logger.setLevel(logging.INFO)
  stream = logging.StreamHandler()
  stream.setFormatter(formatter)
  root_logger.addHandler(stream)

  # Delete previous instance.
  logging.info('Checking for existing dev server instances...')
  instances = vultr.get_instances()
  old_instance = next(
      (x for x in instances if x['label'] == DEV_SERVER_NAME), None)
  if old_instance is not None and old_instance['server_status'] == 'locked':
    logging.error('Server is locked, try again later.')
    sys.exit(1)

  if old_instance is not None:
    old_instance_id = old_instance['id']
    logging.info(f'Found instance {old_instance_id}. Deleting...')
    vultr.delete_instance(old_instance_id)
    logging.info('Deleted previous instance.')
  else:
    logging.info('No existing instance found.')

  # Get ID of the latest backup.
  logging.info('Getting latest backup ID...')
  backups = vultr.get_backups()
  viable_backups = (x for x in backups
                    if SERVER_LABEL in x['description']
                        and x['status'] == 'complete')
  latest = sorted(viable_backups, key=lambda x: x['date_created'], reverse=True)[0]
  backup_id = latest['id']
  logging.info(f'Found backup {backup_id} made on {latest["date_created"]}.')

  # Create the new instance.
  logging.info(f'Creating new {DEV_SERVER_NAME} instance...')
  instance = vultr.create_instance(
      region='lax', plan='vc2-1c-1gb', snapshot_id=backup_id,
      firewall_group_id=DEV_FIREWALL_GROUP, label=DEV_SERVER_NAME)
  logging.info(f'Created new {DEV_SERVER_NAME} instance.')
  dev_instance_id = instance['id']

  # Wait for the instance to be up.
  logging.info(f'Waiting for server to be operational...')
  while True:
    time.sleep(5)
    instance = vultr.get_instance(dev_instance_id)
    if instance['server_status'] in ['none', 'locked']:
      print('.', end='')
      continue
    if instance['server_status'] != 'ok':
      logging.error(f'Detected bad server status "{instance["server_status"]}".')
      sys.exit(1)
    break
  logging.info(f'Server is ready at {instance["main_ip"]}.')

  # Run finalization playbook.
  playbook_vars = {'host_ip': instance["main_ip"], 'hostname': DEV_SERVER_NAME}
  subprocess.run(
    ['ansible-playbook',
     f'{scripts_dir}/dev-server-setup.yml',
     '-i', instance["main_ip"] + ',',
     '-u', ANSIBLE_USER,
     '-e', json.dumps(playbook_vars)],
    check=True) 
  logging.info('All done.')


if __name__ == '__main__':
  main()