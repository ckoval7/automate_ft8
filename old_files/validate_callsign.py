import re

callsign = 'VE1/KC3CPK/P'

def validate_callsign(callsign):
    chk_callsign = re.search('((\d|[A-Z])+\/)?((\d|[A-Z]){3,})(\/(\d|[A-Z])+)?(\/(\d|[A-Z])+)?$',
            callsign)
    pfx = chk_callsign.group(1).strip('/')
    call = chk_callsign.group(3)
    sfx = chk_callsign.group(5).strip('/')
    if chk_callsign.group() != '':
        print(pfx)
        print(call)
        print(sfx)
    else:
        print("Invalid Callsign")

validate_callsign(callsign)
