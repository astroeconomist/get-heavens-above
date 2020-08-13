from datetime import datetime
import datetime as dt
import time
from math import floor
from math import sin, cos, acos, asin, pi, tan, atan, atan2

BJLON = 116.3142984
BJLAT = 39.9906708
SIT = 1.002737909350975
'''
基本计算与换算
'''


def rad2deg(rad):
    return rad / pi * 180


def deg2rad(deg):
    return deg / 180 * pi


def h2hms(time):
    h = floor(time)
    m = floor((time-h) * 60)
    s = (time-h-m/60) * 3600
    return "%2d:%2d:%4.2f" % (h, m, s)


def getjd(time):  # 计算儒略日，输入datetime类型，输出浮点数
    y = time.year if time.month > 2 else time.year - 1
    m = time.month-3 if time.month > 2 else time.month + 12
    d = time.day
    h = time.hour
    minute = time.minute
    s = time.second + time.microsecond / 1000000
    jd = 1721103.5 + floor(365.25 * y) + floor(30.60 *
                                               m + 0.5) + d + h/24 + minute / (24*60) + s/86400
    return jd


def get_date_jd(time):  # 计算零时的儒略日，输入datetime类型，输出浮点数
    y = time.year if time.month > 2 else time.year - 1
    m = time.month-3 if time.month > 2 else time.month + 12
    d = time.day
    jd = 1721103.5 + floor(365.25 * y) + floor(30.60 * m + 0.5) + d
    return jd


def getsittime(jd, lon):  # 计算恒星时，输入儒略日和经度，输出角度制恒星时
    t = jd-2451544.5
    return (99.967794687 + t * (360.98564736628603 + t * (2.907879e-13 - 5.302e-22 * t)) + lon) % 360


def getsit(jd, lon):  # 计算恒星时，输入儒略日和经度，输出hh:mm:ss.ss
    sit = getsittime(jd, lon) / 15
    sith = floor(sit)
    sitm = floor(sit * 60 % 60)
    sits = sit * 3600 % 60
    return ("%2d:%2d:%4.2f" % (sith, sitm, sits))


'''
球面三角相关变换
'''


def equ2h(ra, dec, lat, sit):  # 赤道坐标(赤经, 赤纬, 纬度, 恒星时)转地平高度角h
    ra = deg2rad(ra)
    dec = deg2rad(dec)
    lat = deg2rad(lat)
    sit = deg2rad(sit)
    return rad2deg(asin(sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(sit - ra)))


def equ2a(ra, dec, lat, sit):  # 赤道坐标(赤经, 赤纬, 纬度, 恒星时)转方位角h，正北为0，正东为90
    ra = deg2rad(ra)
    dec = deg2rad(dec)
    lat = deg2rad(lat)
    sit = deg2rad(sit)
    return (rad2deg(atan2(sin(sit - ra), (cos(sit - ra) * sin(lat) - tan(dec) * cos(lat))))) % 360



'''
太阳相关计算
'''


def sun_ecl_lon(jd):  # 计算太阳黄经，误差0.01°
    t = (jd - 2451545.0) / 36525
    l0 = 280.46645 + t * (36000.76983 + t * 0.0003032)
    m = 357.52910 + t * (35999.05030  + t * (- 0.0001559 - t * 0.00000048))
    m = deg2rad(m)  # 化为弧度
    c = (1.914600 - t * (0.004817 + 0.000014 * t)) * sin(m) +\
        (0.019993 - 0.000101 * t) * sin(2 * m) +\
        0.000290 * sin(3*m)
    return (l0 + c) % 360
    # return c


def sun_ecl_lon_j2000(jd):  # 计算按J2000历元的太阳黄经，误差0.01°
    return sun_ecl_lon(jd) - 1.397 * (jd - 2451545.0) / 36525


def ecl_obl(jd):  # 计算黄赤交角，单位度
    t = (jd - 2451545.0) / 36525
    sec = 21.448 - t * (46.8150 + t * (0.00059 - 0.001813*t))
    return 23 + 26 / 60 + sec / 3600


def sun_ra(jd):  # 计算太阳赤经
    ecl_obl_value = deg2rad(ecl_obl(jd))  # 黄赤交角
    ecl_lon = deg2rad(sun_ecl_lon(jd))  # 太阳黄经
    return rad2deg(atan(cos(ecl_obl_value) * tan(ecl_lon)))


def sun_dec(jd):  # 计算太阳赤纬
    return asin(sin(ecl_obl(jd)/180*pi) * sin(sun_ecl_lon(jd)/180*pi)) / pi * 180


def sun_h(jd, lon, lat):  # 计算太阳高度角
    ra = sun_ra(jd)
    dec = sun_dec(jd)
    sit = getsittime(jd, lon)
    return equ2h(ra, dec, lat, sit)


def sun_a(jd, lon, lat):  # 计算太阳方位角
    ra = sun_ra(jd)
    dec = sun_dec(jd)
    sit = getsittime(jd, lon)
    return equ2a(ra, dec, lat, sit)


'''
较复杂的计算
'''


def sun_transit_time(jd, lon):  # 计算太阳上中天时刻，输入当天UT零点的jd,观测地的经度(东经为正),输出天体上中天的UT(小时)
    t = 0.0  # 平太阳时,单位角度
    ra = sun_ra(jd + t / 360)
    sit = getsittime(jd + t / 360, lon)
    if ra >= sit:
        t = (ra - sit) * SIT
    else:
        t = (ra + 360 - sit) * SIT
    for _ in range(10):
        ra = sun_ra(jd + t / 360)
        sit = getsittime(jd + t / 360, lon)
        t += (ra - sit) * SIT
    return t / 15


def sun_rise_time(jd, lon, lat):  # 计算日出时间，输入当天UT零点的jd,观测地的经度(东经为正),输出UT(小时)
    h0 = deg2rad(-0.8333)
    lat = deg2rad(lat)
    t = 0.0  # 平太阳时,单位角度
    for _ in range(20):
        ra = sun_ra(jd + t / 360)
        dec = deg2rad(sun_dec(jd + t / 360))
        sit = getsittime(jd + t / 360, lon)
        sit1 = ra - \
            rad2deg(acos((sin(h0) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))))
        if sit1 < 0:
            sit1 = 360 + sit1
        t += (sit1 - sit) * SIT
    return t/15

def morning_twilight_time(jd, lon, lat): #计算晨光始时间，输入当天UT零点的jd,观测地的经度(东经为正),输出UT(小时)
    h0 = deg2rad(-18)
    lat = deg2rad(lat)
    t = 0.0  # 平太阳时,单位角度
    for _ in range(10):
        ra = sun_ra(jd + t / 360)
        dec = deg2rad(sun_dec(jd + t / 360))
        sit = getsittime(jd + t / 360, lon)
        sit1 = ra - \
            rad2deg(acos((sin(h0) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))))
        if sit1 < 0:
            sit1 = 360 + sit1
        t += (sit1 - sit) * SIT
    return t/15

def sun_set_time(jd, lon, lat):  # 计算日落时间，输入当天UT零点的jd,观测地的经度(东经为正),输出UT(小时)
    h0 = deg2rad(-0.8333)
    lat = deg2rad(lat)
    t = 0.0  # 平太阳时,单位角度
    for i in range(10):
        ra = sun_ra(jd + t / 360)
        dec = deg2rad(sun_dec(jd + t / 360))
        sit = getsittime(jd + t / 360, lon)
        sit1 = ra + \
            rad2deg(acos((sin(h0) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))))
        if (sit1 < sit and i == 0) or sit1 < 0:
            sit1 = sit1 + 360
        t += (sit1 - sit) * SIT
    return t/15

def evening_twilight_time(jd, lon, lat):  # 计算昏影终时间，输入当天UT零点的jd,观测地的经度(东经为正),输出UT(小时)
    h0 = deg2rad(-18)
    lat = deg2rad(lat)
    t = 0.0  # 平太阳时,单位角度
    for i in range(10):
        ra = sun_ra(jd + t / 360)
        dec = deg2rad(sun_dec(jd + t / 360))
        sit = getsittime(jd + t / 360, lon)
        sit1 = ra + \
            rad2deg(acos((sin(h0) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))))
        if (sit1 < sit and i == 0) or sit1 < 0:
            sit1 = sit1 + 360
        t += (sit1 - sit) * SIT
    return t/15

