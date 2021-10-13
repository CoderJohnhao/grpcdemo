import math
import time

import grpc
from concurrent import futures

import feature_pb2_grpc
import feature_pb2
import feature_db


# 获取地点
def get_feature(db, point):
    for feature in db:
        if feature.location == point:
            return feature
    return None


# 获取坐标点之间的距离
def get_distance(start, end):
    """Distance between two points."""
    coord_factor = 10000000.0
    lat_1 = start.latitude / coord_factor
    lat_2 = end.latitude / coord_factor
    lon_1 = start.longitude / coord_factor
    lon_2 = end.longitude / coord_factor
    lat_rad_1 = math.radians(lat_1)
    lat_rad_2 = math.radians(lat_2)
    delta_lat_rad = math.radians(lat_2 - lat_1)
    delta_lon_rad = math.radians(lon_2 - lon_1)

    a = (pow(math.sin(delta_lat_rad / 2), 2) +
         (math.cos(lat_rad_1) * math.cos(lat_rad_2) * pow(
             math.sin(delta_lon_rad / 2), 2)))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371000
    # metres
    return R * c


class RouteGuide(feature_pb2_grpc.RouteGuideServicer):
    def __init__(self):
        self.db = feature_db.read_feature_db()

    # 根据坐标点返回位置信息
    def GetFeature(self, request, context):
        feature = get_feature(self.db, request)
        print('查询地址信息')
        if feature is None:
            return feature_pb2.Feature(name='没有查到地址', location=request)
        else:
            return feature

    # 位置数组
    def ListFeatures(self, request, context):
        left = min(request.lo.longitude, request.hi.longitude)
        right = max(request.lo.longitude, request.hi.longitude)
        top = max(request.lo.latitude, request.hi.latitude)
        bottom = min(request.lo.latitude, request.hi.latitude)
        print('获取区域内的地点')
        print(left, right, top, bottom)
        for feature in self.db:
            if left <= feature.location.longitude <= right and bottom <= feature.location.latitude <= top:
                if feature.name != "" and feature.name is not None:
                    yield feature

    # 记录路径
    def RecordRoute(self, request_iterator, context):
        point_count = 0
        feature_count = 0
        distance = 0.0
        prev_point = None
        print("记录路径返回描述")
        start_time = time.time()
        for point in request_iterator:
            point_count += 1
            if get_feature(self.db, point):
                feature_count += 1
            if prev_point:
                distance += get_distance(prev_point, point)
            prev_point = point
        elapsed_time = time.time() - start_time
        return feature_pb2.RouteSummary(
            point_count=point_count,
            feature_count=feature_count,
            distance=int(distance),
            elapsed_time=int(elapsed_time)
        )

    # 路径聊天
    def RouteChat(self, request_iterator, context):
        prev_notes = []
        for new_note in request_iterator:
            # for prev_note in prev_notes:
            print("聊天" + new_note.message)
            #     yield prev_note
            # prev_notes.append(new_note)
            new_note.message = "我收到你的消息：" + new_note.message
            yield new_note


def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    feature_pb2_grpc.add_RouteGuideServicer_to_server(RouteGuide(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('server running')
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run()
