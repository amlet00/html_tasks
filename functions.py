def get_spn(toponym):
    lower_longitude, lower_lattitude = map(float, toponym["boundedBy"]["Envelope"]["lowerCorner"].split(" "))
    upper_longitude, upper_lattitude = map(float, toponym["boundedBy"]["Envelope"]["upperCorner"].split(" "))
    return upper_longitude - lower_longitude, upper_lattitude - lower_lattitude
