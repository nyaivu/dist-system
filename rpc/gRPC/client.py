import grpc
import processor_pb2
import processor_pb2_grpc
import auth_helper

def run():
    # 1. Dapatkan Token JWT
    token = auth_helper.generate_token()
    
    # 2. Buka Channel ke Server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = processor_pb2_grpc.ProcessorServiceStub(channel)

        # --- Test Counter ---
        print("--- Testing gRPC Counter ---")
        response = stub.IncrementCounter(processor_pb2.CounterRequest(token=token))
        if response.error_message:
            print(f"Error: {response.error_message}")
        else:
            print(f"Counter berhasil diupdate! Nilai sekarang: {response.count}")

        # --- Test Upload Gambar ---
        print("\n--- Testing gRPC Upload ---")
        img_path = "test_image.jpg" # Pastikan file ini ada
        try:
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            
            req = processor_pb2.FileRequest(
                file_content=img_bytes,
                file_name=img_path,
                token=token
            )
            res = stub.UploadFile(req)
            
            if res.error_message:
                print(f"Server Error: {res.error_message}")
            else:
                print(f"Berhasil! Format: {res.format}, Res: {res.resolution}, Size: {res.size_kb:.2f} KB")
        except FileNotFoundError:
            print("File gambar tidak ditemukan untuk diupload.")

if __name__ == '__main__':
    run()