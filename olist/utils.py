import numpy as np

def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Dünya üzerindeki iki nokta arasındaki mesafeyi (KM) hesaplar.
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return c * 6371
