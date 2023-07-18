# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
import re
import datetime

PATTERN = re.compile(r"(?P<value>\d+)(?P<modifier>[дгчмсdyhms])")
LINE_PATTERN = re.compile(r"^(\d+[дгчмсdyhms]){1,}$")

MODIFIERS = {
	"д": datetime.timedelta(days=1),
	"г": datetime.timedelta(days=365),
	"ч": datetime.timedelta(hours=1),
	"м": datetime.timedelta(minutes=1),
	"с": datetime.timedelta(seconds=1),
    "d": datetime.timedelta(days=1),
	"y": datetime.timedelta(days=365),
    "h": datetime.timedelta(hours=1),
    "m": datetime.timedelta(minutes=1),
    "s": datetime.timedelta(seconds=1)
}

def parse_timedelta(value: str):
	match = LINE_PATTERN.match(value)
	if not match:
		raise Exception("Неправильний формат часу")
	try:
		result = datetime.timedelta()
		for match in PATTERN.finditer(value):
			value, mod = match.groups()
			result += int(value) * MODIFIERS[mod]
	except:
		raise Exception("Значение слишком великое")
	return result

def get_duration_and_reason(args: str):
	if not args:
		return None, None
	if len(args) == 1:
		return parse_timedelta(args[0]), None
	else:
		return parse_timedelta(args[0]), " ".join(args[1:])
