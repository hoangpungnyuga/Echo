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

~~ По поводу того как сделать себя админом, вы можете вручную себя добавить в датабазе data/ db.sql (файл будет создан после запуска, или создайте сами. touch data/db.sql)<br>
~~ Для этого откройте файл датабазы любой программой, к примеру SQLiteStudio<br>
~~ И добавьте свой ID в таблицу admins, в name (имя текст кнопки, к примеру ADMIN), rights ( mute\;purge\;warn\;view\;promote\;ban )<br>
После рестарт.

## Команды есть в /help

По вопросам писать мне в лс, в профиле есть ссылка.
