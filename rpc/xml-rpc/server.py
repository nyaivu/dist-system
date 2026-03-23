from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import auth_helper
import json
import os
import io
from PIL import Image
from threading import Lock

class XMLRPCServer:
    def __init__(self):
        self.lock = Lock()
        self.storage_file = "../../storage.json" # Path ke file storage bersama
        self.upload_dir = "uploads"
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def execute_action(self, token, action, data=None):
        # 1. Validasi Token (Keamanan & Expiry)
        is_valid, msg = auth_helper.verify_token(token)
        if not is_valid:
            return {"status": "error", "code": 401, "message": msg}

        # 2. Routing Action
        if action == "get_counter":
            return self._handle_counter()
        elif action == "upload":
            return self._handle_upload(data)
        else:
            return {"status": "error", "code": 404, "message": "Action not found"}

    def _handle_counter(self):
        # 3. State Management (Persistent & Thread-safe)
        with self.lock:
            with open(self.storage_file, 'r+') as f:
                content = json.load(f)
                content["counter"] += 1
                f.seek(0)
                json.dump(content, f)
                f.truncate()
                return {"status": "success", "new_value": content["counter"]}

    def _handle_upload(self, data):
        try:
            # 4. Handle XML-RPC Binary Data
            # Data yang dikirim client otomatis dibungkus xmlrpc.client.Binary
            file_bytes = data.data 
            
            # Ekstrak Metadata
            img = Image.open(io.BytesIO(file_bytes))
            metadata = {
                "format": img.format,
                "resolution": f"{img.width}x{img.height}",
                "size_kb": len(file_bytes) / 1024
            }

            # Simpan file
            save_path = os.path.join(self.upload_dir, "uploaded_xml.png")
            with open(save_path, "wb") as f:
                f.write(file_bytes)

            return {"status": "success", "metadata": metadata}
        except Exception as e:
            return {"status": "error", "code": 400, "message": str(e)}

# Jalankan Server
if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 9000))
    server.register_instance(XMLRPCServer())
    print("XML-RPC Server berjalan di port 9000...")
    server.serve_forever()