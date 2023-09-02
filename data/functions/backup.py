# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
from loader import bot, chat_backup
from aiogram.types import InputFile
from data.functions.models import Connect
from datetime import datetime, timedelta
from wipe import create_file
import os
import asyncio
import zipfile
import pyzipper
import secrets
import string

def generate_random_hash():
    alphabet = string.ascii_letters
    random_hash = ''.join(secrets.choice(alphabet) for _ in range(5))
    return random_hash

async def backup_database():
    print("Created backup .sql , replies.json")
    while True:
        random_hash = generate_random_hash()
        # Name dir
        backup_dir = "backup"
        try:
            # Get the database connection details from the Connect class
            db_name = Connect.get("database", "")
            db_user = Connect.get("user", "")
            db_pass = Connect.get("password", "")
            db_host = Connect.get("host", "")
            db_port = Connect.get("port", "")

            # Create the backup directory if it doesn't exist
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Generate the backup file name
            backup_file = os.path.join(backup_dir, f"{datetime.now().strftime('%d-%m-%y_%H-%M-%S')}_{db_name}.sql.bak")

            # Run the pg_dump command to create the backup
            command = f"pg_dump -U {db_user} -h {db_host} -p {db_port} -F c -b -f {backup_file} {db_name}"
            process = await asyncio.create_subprocess_exec(
                "bash", "-c", f"export PGPASSWORD={db_pass}; {command}"
            )
            await process.wait()

            print(f"Local database backup created: {backup_file}"
                  "\nStarting create in 7zip archive and send chat_backup")

            archive_name = '%s/архив_%s.zip' % (backup_dir, random_hash)
            replies_db = 'data/replies.json'

            cus_date = {
                # Это кастомное дата-время для файла(чтобы так отображало в посл. изменение файла в архиве)
                "year":     1980, # Год
                "month":    1,    # Месяц
                "day":      1,    # День
                "hour":     4,    # Час
                "minute":   20,   # Минут
                "second":   0,    # Секунд
                "tzinfo": None
            }

            new_date = datetime(**cus_date)
            new_date += timedelta(hours=1)  # Add one hour to the new_date

            sqlbak = "/project/%s/main/bk/sql/%s" % (db_name, backup_file)
            repliesbak = "/project/%s/main/bk/msgs/%s" % (db_name, replies_db)

            # Create a temporary copy of the file with the modified date
            os.utime(backup_file, (new_date.timestamp(), new_date.timestamp()))
            os.utime(replies_db, (new_date.timestamp(), new_date.timestamp()))

            with pyzipper.AESZipFile(archive_name, 'w', compression=zipfile.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as myzip:
                myzip.setpassword(db_pass.encode())
                myzip.write(backup_file, arcname=sqlbak)

                if not os.path.exists(replies_db):
                    await create_file(replies_db)

                myzip.write(replies_db, arcname=repliesbak)

                os.remove(backup_file)

            try:
                formatted_date = datetime.now().strftime('%d-%m-%y %H:%M:%S')

                text = (f"<i>Backup database({db_name})\n"
                        f"timestamp: {formatted_date}</i>")
                # And send backup_file in chat_backup(config.ini)
                await bot.send_document(chat_backup, document=InputFile(archive_name), caption=text)
                print('Done.')
            except Exception as e:
                print(f"Отправить {chat_backup} {archive_name} не удалось, по причине: {e}")

            # Sleep for 2 hours before performing the next backup
            await asyncio.sleep(timedelta(hours=2).total_seconds())
        except Exception as e:
            print(f"Создать бэкап вашей базы данных в /{backup_dir} не удалось, по причине: {e}\n"
                   "Возможно, вам стоит выполнить `sudo apt install postgresql-client postgresql-client-common libpq-dev pyzipper`")
            break
