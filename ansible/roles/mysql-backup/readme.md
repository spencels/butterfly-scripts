# Backup Strategy

Backups are handled by a daily cron job, `backup_mysql.py`, which dumps the
database using mysqlpump and uploads the dump to Vultr block storage.

A separate cron job, `archive_backup.py`, reads the block storage buckets and
deletes older dumps if there are more than 3 available.