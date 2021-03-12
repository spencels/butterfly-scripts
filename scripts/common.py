import logging
import pathlib

import vultr

# Hard-coded values about the local environment.
PROD_SERVER_LABEL = 'adhdbutts-wp'
DEV_SERVER_NAME = 'butts-dev'
DEV_FIREWALL_GROUP = 'ba498c9a-106c-41b2-881a-144795427b90'
ANSIBLE_USER = 'spencels'

def configure_logging(debug=False):
  formatter = logging.Formatter(
      '%(levelname)-1.1s %(asctime)s: %(message)s',
      '%H:%M:%S')
  root_logger = logging.getLogger()
  root_logger.setLevel(logging.INFO if not debug else logging.DEBUG)
  stream = logging.StreamHandler()
  stream.setFormatter(formatter)
  root_logger.addHandler(stream)

def stop_dev_server():
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