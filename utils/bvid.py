import re

table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr = {}
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608
for index in range(58):
    tr[table[index]] = index

def av_to_bv(av: str) -> str:
    x = int(av[2:])
    x = (x ^ xor) + add
    r = list('BV1  4 1 7  ')
    for i in range(6):
        r[s[i]] = table[x // 58 ** i % 58]
    return ''.join(r)

def bv_to_av(bv: str) -> str:
    r = 0
    for i in range(6):
        r += tr[bv[s[i]]] * 58**i
    return "av{}".format((r - add) ^ xor)

def get_bv(vid: str) -> str:
    search_bv = re.search("BV[0-9a-zA-Z]+", vid, re.IGNORECASE)
    if search_bv is not None:
        return search_bv.group(0)
    search_av = re.search("av[0-9]+", vid, re.IGNORECASE)
    if search_av is not None:
        return av_to_bv(search_av.group(0))
    return vid