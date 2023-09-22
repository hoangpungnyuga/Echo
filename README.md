# Echo
 
### Чтобы установить данного бота пропишите в терминал -
```shell
apt-get update -y
apt-get install git python3 python3-pip -y
git clone https://github.com/hoangpungnyuga/Echo
cd Echo
pip install -r requirements.txt
```
## После измените название файла в папке **data/** example.config.ini на **config.ini**
Это можно сделать так:
```shell
mv example.config.ini config.ini
```

### После измените **config.ini** на свои значения.

## Чтобы после запустить бота выполните в терминале -
```shell
python3 bot.py
```

~~ По поводу того как сделать себя админом, вы можете вручную себя добавить в датабазе data/ db.sql
~~ Для этого откройте файл датабазы любой программой, к примеру (SQLiteStudio)[https://sqlitestudio.pl/]
~~ И добавьте свой ID в таблицу admins в rights ( mute\;purge\;warn\;view\;promote\;ban )
# После рестарт.

## Команды есть в /help