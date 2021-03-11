#!/usr/bin/env python3
"""Back up MySql database to Object Storage.

Can be run as a cron job or one-off.
Requires mysqldump, s3cmd.
"""
import config
import logging
import pathlib
import subprocess
import sys
import time
import optparse
import tempfile
import os

import urllib

# Flags
def generate_flags():
  parser = optparse.OptionParser()
  parser.add_option('--mysql_dump_path', dest='mysql_dump_path')
  parser.add_option('--prod', dest='prod', action='store_true')
  return parser.parse_args()[0]
flags = generate_flags()

project_dir = pathlib.Path(__file__).parent.absolute()
run_mysqldump_script_path = project_dir.joinpath('run-mysqldump.sh')
s3cfg = project_dir.joinpath('.s3cfg')

def dump_database(backup_file):
  """Dumps Mysql database backup to the provided path."""
  logging.info(f'Dumping database to {backup_file}')
  with open(backup_file, 'wb') as f:
    # Ideally this could be done with shell=True but Python doesn't seem to
    # pipe the error code through when the shell command uses ">" redirection.
    cmd = [
      run_mysqldump_script_path,
      config.mysql_user,
      config.mysql_password,
      backup_file]
    process = subprocess.run(cmd, stderr=subprocess.PIPE)
  logging.info(f'mysqldump stderr:\n{process.stderr.decode("utf-8")}')
  if process.returncode != 0:
    logging.fatal(f'mysqldump failed with return code {process.returncode}')
    sys.exit(1)

  logging.info(f'Finished dumping database.')


def upload_to_s3(dump_file):
  """Upload file at the provided path to S3."""
    dest = f's3://butterflies/{"" if flags.prod else "test/"}mysql-backups/{backup_file.name}'
    logging.info(f'Uploading to Object Storage at {dest}.')
    # Use the default .s3cfg for non-prod.
    config_flag = f'-c"{s3cfg}"' if flags.prod else ''
    subprocess.run(
        f'/usr/bin/s3cmd {config_flag} put {backup_file} {dest}',
        shell=True, check=True)
    logging.info('Upload finished.')

def main():
  logging.info('*** Beginning backup.')
  with tempfile.TemporaryDirectory('mysqlbackup') as tempdirname:
    tempdir_path = pathlib.Path(tempdirname)

    # Dump the database, or use the provided dump path.
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    if flags.mysql_dump_path:
      backup_file = pathlib.Path(flags.mysql_dump_path)
      if not backup_file.exists():
        raise ValueError(f'No file exists at {backup_file}')
      logging.info(f'Skipping database dump, using file at {backup_file}')
    else:
      backup_file = tempdir_path.joinpath(f'backup-{timestamp}.sql.gz')
      dump_database(backup_file)




def configure_logging():
  logFormatter = logging.Formatter(
      '%(levelname)-1.1s %(asctime)s %(filename)s:%(lineno)d: %(message)s')
  rootLogger = logging.getLogger()
  rootLogger.setLevel(logging.INFO)
  fileHandler = logging.FileHandler('/var/log/mysql_backup.log')
  fileHandler.setFormatter(logFormatter)
  rootLogger.addHandler(fileHandler)
  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(logFormatter)
  rootLogger.addHandler(consoleHandler)


if __name__ == '__main__':
  configure_logging()
  try:
    main()
  except Exception:
    logging.exception('Unexpected fatal exception')
    sys.exit(1)