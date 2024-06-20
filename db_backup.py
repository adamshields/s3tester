import os
import sys
import tempfile
import asyncio
import mysql.connector
from datetime import datetime
import logging
import argparse
import json
from mysql.connector import Error

"""
Database Backup Script
======================

This script performs backups and restores of a MySQL database, including individual table backups.
It also includes functionality to copy data between databases on different servers and environments.

Example Commands:
-----------------
1. Backup version 1.0.0 from dev environment:
   python db_backup.py --version 1.0.0 --source-env dev

2. Restore the entire database from a backup file:
   python db_backup.py --version 1.0.0 --source-env dev --restore-file ./backups/1.0.0/dev/FULL_breaker19er_backup.sql

3. Restore a specific table from a backup file:
   python db_backup.py --version 1.0.0 --source-env dev --restore-file ./backups/1.0.0/dev/tables/breaker19er_table_name_backup.sql --restore-table-name table_name

4. Copy data from dev environment to test environment:
   python db_backup.py --copy-data --source-env dev --target-env test

5. Copy a specific table from dev environment to test environment:
   python db_backup.py --copy-data --source-env dev --target-env test --table-name table_name
"""

# Load configuration from config file
with open('config.json') as config_file:
    config = json.load(config_file)

# Backup directory configuration
BACKUP_DIR = './backups'

def setup_logging(log_dir):
    """ Set up logging configuration """
    log_file = os.path.join(log_dir, 'db_backup.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

async def run_command(command):
    """ Run a shell command asynchronously """
    logging.info(f"Running command: {command}")
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    output, error = await process.communicate()
    if process.returncode != 0:
        logging.error(f"Command failed: {command}\nError: {error.decode()}\nOutput: {output.decode()}")
        raise Exception(f"Command failed: {command}\nError: {error.decode()}\nOutput: {output.decode()}")
    return output.decode()

async def backup_database(backup_dir, db_config):
    """ Backup the entire database """
    backup_file = os.path.join(backup_dir, f"FULL_{db_config['database']}_backup.sql")
    command = f"mysqldump -h {db_config['host']} -P {db_config['port']} -u {db_config['user']} -p{db_config['password']} {db_config['database']} > {backup_file}"
    await run_command(command)
    logging.info(f"Database backup completed: {backup_file}")

async def backup_table(table_name, backup_file, db_config):
    """ Backup a single table """
    command = f"mysqldump -h {db_config['host']} -P {db_config['port']} -u {db_config['user']} -p{db_config['password']} {db_config['database']} {table_name} > {backup_file}"
    await run_command(command)
    logging.info(f"Table backup completed: {backup_file}")

async def backup_tables(backup_dir, db_config):
    """ Backup each table individually """
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_backup_dir = os.path.join(backup_dir, 'tables')
        os.makedirs(table_backup_dir, exist_ok=True)
        tasks = []
        for (table_name,) in tables:
            backup_file = os.path.join(table_backup_dir, f"{db_config['database']}_{table_name}_backup.sql")
            tasks.append(backup_table(table_name, backup_file, db_config))
        await asyncio.gather(*tasks)
        cursor.close()
        connection.close()
    except Error as e:
        logging.error(f"Error while connecting to MySQL: {e}")
        raise

async def restore_database(backup_file, db_config):
    """ Restore the entire database from a backup file """
    command = f"mysql -h {db_config['host']} -P {db_config['port']} -u {db_config['user']} -p{db_config['password']} {db_config['database']} < {backup_file}"
    await run_command(command)
    logging.info(f"Database restored from backup: {backup_file}")

async def restore_table(table_name, backup_file, db_config):
    """ Restore a specific table from a backup file """
    command = f"mysql -h {db_config['host']} -P {db_config['port']} -u {db_config['user']} -p{db_config['password']} {db_config['database']} < {backup_file}"
    await run_command(command)
    logging.info(f"Table {table_name} restored from backup: {backup_file}")

async def copy_data_between_databases(source_env, target_env, table_name=None):
    """ Copy data from the source database to the target database """
    try:
        source_db_config = config[source_env]
        target_db_config = config[target_env]

        # Create a temporary backup file
        temp_dir = tempfile.gettempdir()
        temp_backup_file = os.path.join(temp_dir, f"{source_db_config['database']}_temp_backup.sql")

        # Backup the source database or table
        if table_name:
            command = f"mysqldump -h {source_db_config['host']} -P {source_db_config['port']} -u {source_db_config['user']} -p{source_db_config['password']} {source_db_config['database']} {table_name} > {temp_backup_file}"
        else:
            command = f"mysqldump -h {source_db_config['host']} -P {source_db_config['port']} -u {source_db_config['user']} -p{source_db_config['password']} {source_db_config['database']} > {temp_backup_file}"
        await run_command(command)
        logging.info(f"Temporary backup of source database completed: {temp_backup_file}")

        # Restore the backup to the target database or table
        command = f"mysql -h {target_db_config['host']} -P {target_db_config['port']} -u {target_db_config['user']} -p{target_db_config['password']} {target_db_config['database']} < {temp_backup_file}"
        await run_command(command)
        logging.info(f"Data copied to target database from backup: {temp_backup_file}")

        # Clean up the temporary backup file
        os.remove(temp_backup_file)
        logging.info(f"Temporary backup file removed: {temp_backup_file}")
    except Exception as e:
        logging.error(f"An error occurred while copying data between databases: {e}")
        raise

async def main(version=None, restore_file=None, restore_table_name=None, copy_data=False, source_env=None, target_env=None, table_name=None):
    """ Main function to perform backup, restore, and copy operations """
    try:
        # Ensure source environment is provided for backup and restore operations
        if not copy_data and not source_env:
            raise ValueError("Source environment must be specified for backup and restore operations.")
        
        if copy_data:
            # Set up logging for data copying operations
            env_dir = f"{source_env}_to_{target_env}"
            backup_dir = os.path.join(BACKUP_DIR, env_dir, datetime.now().strftime('%Y%m%d%H%M%S'))
            os.makedirs(backup_dir, exist_ok=True)
            setup_logging(backup_dir)
            await copy_data_between_databases(source_env, target_env, table_name)
        else:
            # Define backup directory for backup and restore operations
            env_dir = os.path.join(version, source_env)
            backup_dir = os.path.join(BACKUP_DIR, env_dir)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            else:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                backup_dir = os.path.join(backup_dir, timestamp)
                os.makedirs(backup_dir, exist_ok=True)

            # Set up logging for backup and restore operations
            setup_logging(backup_dir)

            if restore_file:
                if restore_table_name:
                    await restore_table(restore_table_name, restore_file, config[source_env])
                else:
                    await restore_database(restore_file, config[source_env])
            else:
                await backup_database(backup_dir, config[source_env])
                await backup_tables(backup_dir, config[source_env])
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Database Backup, Restore, and Copy Script')
    parser.add_argument('--version', type=str, help='Version of the release (e.g., 1.0.0)', required='--copy-data' not in sys.argv)
    parser.add_argument('--source-env', type=str, help='Source environment (e.g., dev, test, prod)', required='--copy-data' not in sys.argv)
    parser.add_argument('--restore-file', type=str, help='Path to the backup file to restore')
    parser.add_argument('--restore-table-name', type=str, help='Name of the table to restore from the backup file')
    parser.add_argument('--copy-data', action='store_true', help='Copy data from source to target database')
    parser.add_argument('--target-env', type=str, help='Target environment (e.g., dev, test, prod)', required='--copy-data' in sys.argv)
    parser.add_argument('--table-name', type=str, help='Name of the table to copy (optional)')
    args = parser.parse_args()
    asyncio.run(main(args.version, args.restore_file, args.restore_table_name, args.copy_data, args.source_env, args.target_env, args.table_name))
