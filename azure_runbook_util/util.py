import datetime
import json

import pytz

_DEFAULT_TIMEZONE = "Europe/Madrid"


def time_in_range(start: int, end: int, current_time: int) -> bool:
    """ Return true if current_time is in the range [start, end] """
    if start <= end:
        return start <= current_time < end
    else:
        return start <= current_time or current_time <= end


def get_now_for_timezone(timezone: str = _DEFAULT_TIMEZONE) -> datetime:
    """
    Get the current 'datetime' for the given timezone
    :param timezone:
    :return:
    """
    utc = pytz.utc
    utc_dt = utc.localize(datetime.datetime.utcnow())
    now_timezone = pytz.timezone(timezone)

    return utc_dt.astimezone(now_timezone)


def get_json(message) -> str:
    """
    Get a JSON formatted message
    :param message:
    :return:
    """
    return json.dumps(message)
