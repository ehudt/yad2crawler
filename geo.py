from math               import radians, sin, cos, atan2, sqrt

def haversine_distance(s, t):
    lat1, lon1 = s
    lat2, lon2 = t

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return c * 6371