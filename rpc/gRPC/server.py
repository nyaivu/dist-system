import grpc
from concurrent import futures
import processor_pb2
import processor_pb2_grpc
import auth_helper # Pastikan file ini bisa diakses (pindah ke folder ini atau setup path)
import json
import io
import os
from PIL import Image
from threading import Lock

class ProcessorServicer(processor_pb2_grpc.ProcessorServiceServicer):
    def __init__(self):
        self.lock = Lock()
        self.storage_file = "../../storage.json" # Sesuaikan path ke root
        self.upload_dir = "uploads"
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def IncrementCounter(self, request, context):
        # 1. Validasi Token (Kriteria Keamanan)
        is_valid, msg = auth_helper.verify_token(request.token)
        if not is_valid:
            return processor_pb2.CounterResponse(error_message=msg)

        # 2. Update Counter (Persistent & Race Condition Safe)
        with self.lock:
            with open(self.storage_file, 'r+') as f:
                data = json.load(f)
                data["counter"] += 1
                f.seek(0)
                json.dump(data, f)
                f.truncate()
                return processor_pb2.CounterResponse(count=data["counter"])

    def UploadFile(self, request, context):
        # 1. Validasi Token
        is_valid, msg = auth_helper.verify_token(request.token)
        if not is_valid:
            return processor_pb2.FileResponse(error_message=msg)

        try:
            # 2. Simpan file biner ke disk
            save_path = os.path.join(self.upload_dir, request.file_name)
            with open(save_path, "wb") as f:
                f.write(request.file_content)

            # 3. Ekstrak Metadata menggunakan Pillow
            img = Image.open(io.BytesIO(request.file_content))
            return processor_pb2.FileResponse(
                format=img.format,
                size_kb=len(request.file_content) / 1024,
                resolution=f"{img.width}x{img.height}"
            )
        except Exception as e:
            return processor_pb2.FileResponse(error_message=f"Gagal: {str(e)}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    processor_pb2_grpc.add_ProcessorServiceServicer_to_server(ProcessorServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server berjalan di port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()