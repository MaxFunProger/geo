def map_size(toponym):
    return [str(int(toponym["boundedBy"]["Envelope"]["upperCorner"][0]) - int(toponym["boundedBy"]["Envelope"]["lowerCorner"][0])),
            str(int(toponym["boundedBy"]["Envelope"]["upperCorner"][1]) - int(toponym["boundedBy"]["Envelope"]["lowerCorner"][1]))]
