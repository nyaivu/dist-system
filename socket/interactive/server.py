from xmlrpc.server import SimpleXMLRPCServer
import json
import os
import base64
from PIL import Image
import io
import auth_helper

class TraditionalRPCServer:
    def __init__(self):
        self.storage_file = "storage.json"
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump({"counter": 0}, f)

    def _update_counter(self):
        with open(self.storage_file, 'r+') as f:
            data = json.load(f)
            data["counter"] += 1
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        return data["counter"]

    def call_function(self, token, func_name, params=None):
        # 1. Implementasi Keamanan (Token/JWT)
        is_valid, msg = auth_helper.verify_token(token)
        if not is_valid:
            return {"status": "error", "code": 401, "message": msg}

        # 2. Routing Fungsi & Counter
        if func_name == "increment":
            new_val = self._update_counter()
            return {"status": "success", "counter": new_val}

        elif func_name == "upload_image":
            return self.process_image(params)

        else:
            # Error Handling & Parameter Validation
            return {"status": "error", "code": 404, "message": "Method not found"}

    def process_image(self, b64_data):
        try:
            # 3. RPC File Transfer & Metadata
            img_data = base64.b64decode(b64_data)
            img = Image.open(io.BytesIO(img_data))
            
            metadata = {
                "format": img.format,
                "size_kb": round(len(img_data) / 1024, 2),
                "resolution": f"{img.width}x{img.height}"
            }
            return {"status": "success", "metadata": metadata}
        except Exception as e:
            return {"status": "error", "code": 400, "message": f"Invalid image data: {str(e)}"}

# Jalankan Server
server = SimpleXMLRPCServer(("localhost", 8000))
server.register_instance(TraditionalRPCServer())
print("Server Traditional RPC berjalan di port 8000...")
server.serve_forever()