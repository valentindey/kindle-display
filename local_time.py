from datetime import datetime

import pytz

UTC = pytz.timezone('UTC')
CET = pytz.timezone('CET')


def now_cet():
    return utc_to_cet(datetime.now())


def utc_to_cet(dt):
    # translates the given time to CET
    # setting the right locale would be easier but a bigger hassle to
    # make it work on the kindle also this is not a very flexible way
    # to handle the different time zones, but good enough for my use
    # case
    localized_utc = UTC.localize(dt)
    return localized_utc.astimezone(CET)


def cet_to_utc(dt):
    localized_cet = CET.localize(dt)
    return localized_cet.astimezone(UTC)


def as_cet(dt):
    return CET.localize(dt)
