import json
import feature_pb2

def read_feature_db():
    features = []
    with open('route_guide_db.json') as f:
        for item in json.load(f):
            feature = feature_pb2.Feature(
                name=item['name'],
                location=feature_pb2.Point(
                    latitude=item['location']['latitude'],
                    longitude=item['location']['longitude']
                )
            )
            features.append(feature)
    return features
