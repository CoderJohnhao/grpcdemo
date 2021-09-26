import os
import sys
from io import BytesIO
from PIL import Image

import grpc
import helloworld_pb2 as pb2
import helloworld_pb2_grpc as pb2_grpc
import time
from concurrent import futures


class HelloServer(pb2_grpc.HelloServer):
    def Hello(self, request, context):
        name = request.name
        print(name)
        result = f'My name is {name}, hello world! - String'
        return pb2.HelloResponse(result=result)

    def Test(self, request, context):
        data = request.param
        name = str(data, encoding='utf-8')
        print(name)
        result = f'My name is {name}, hello world! - Data'
        return pb2.HelloResponse(result=result)

    def Upload(self, request, context):
        data = request.data
        # 将bytes结果转化为字节流
        bytes_stream = BytesIO(data)
        # 读取到图片
        roiimg = Image.open(bytes_stream)
        imgByteArr = BytesIO()  # 初始化一个空字节流
        type = request.type.upper()
        if request.type.strip() == '' or '.' in request.type:
            type = 'PNG'
        roiimg.save(imgByteArr, format(type))  # 把我们得图片以‘PNG’保存到空字节流
        imgByteArr = imgByteArr.getvalue()  # 无视指针，获取全部内容，类型由io流变成bytes。
        path = os.path.abspath('')
        image_path = os.path.join(path, request.name)
        with open(image_path, 'wb') as f:
            f.write(imgByteArr)
        return pb2.HelloResponse(result=image_path)

def run():
    grpc_server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4)
    )
    pb2_grpc.add_HelloServerServicer_to_server(HelloServer(), grpc_server)
    grpc_server.add_insecure_port('0.0.0.0:5000')
    print('server will start')
    grpc_server.start()
    try:
        while 1:
            time.sleep(3600)
    except KeyboardInterrupt:
        grpc_server.stop(0)


if __name__ == '__main__':
    run()