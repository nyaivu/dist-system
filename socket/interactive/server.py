from xmlrpc.server import SimpleXMLRPCServer
import json
import os
import base64
from PIL import Image
import io
import auth_helper

class TraditionalRPCServer:
    def __init__(self):
        # 1. Tentukan nama folder upload
        self.upload_dir = "uploads" 
        
        # 2. Buat foldernya jika belum ada (Penting agar tidak error saat simpan file)
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
            print(f"Folder '{self.upload_dir}' telah dibuat.")

        # 3. Inisialisasi storage counter (seperti yang sudah kamu buat sebelumnya)
        self.storage_file = "storage.json"
        if not os.path.exists(self.storage_file) or os.path.getsize(self.storage_file) == 0:
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

    def upload_image(self, token, file_name, b64_data):
        """Fungsi utama yang dipanggil oleh Client via RPC."""
        
        # 1. Implementasi Keamanan (Token/JWT)
        is_valid, msg = auth_helper.verify_token(token)
        if not is_valid:
            return {"status": "error", "code": 401, "message": msg}

        # 2. Validasi Parameter (Error Handling)
        if not file_name or not b64_data:
            return {"status": "error", "code": 400, "message": "File name dan data gambar tidak boleh kosong."}

        # 3. Panggil Fungsi Internal untuk Memproses Gambar
        result = self._process_image(file_name, b64_data)
        
        if result["status"] == "success":
            # Tampilkan log di console server
            print(f" Berhasil upload & proses: {file_name} ({result['metadata']['resolution']})")
        
        return result

    def _process_image(self, file_name, b64_data):
        """Fungsi internal (helper) untuk decoding, menyimpan, dan ekstraksi metadata."""
        try:
            # a. Decode Base64 kembali ke bytes (biner)
            image_bytes = base64.b64decode(b64_data)
            
            # b. Simpan File ke Disk (Agar ada bukti fisik saat demo)
            save_path = os.path.join(self.upload_dir, file_name)
            with open(save_path, "wb") as f:
                f.write(image_bytes)
            
            # c. Proses dengan Pillow (In-Memory) untuk Metadata
            img = Image.open(io.BytesIO(image_bytes))
            
            # d. Ambil Metadata secara akurat (Kriteria Luar Biasa)
            metadata = {
                "filename": file_name,
                "format": img.format, # Contoh: PNG, JPEG
                "size_kb": f"{len(image_bytes) / 1024:.2f} KB",
                "resolution": f"{img.width}x{img.height}", # Contoh: 1920x1080
                "color_mode": img.mode, # Contoh: RGB, RGBA
                "server_path": save_path # Beritahu client di mana file disimpan
            }
            
            return {"status": "success", "metadata": metadata}
            
        except Exception as e:
            # Jika file corrupt atau bukan gambar, kembalikan error spesifik
            return {"status": "error", "code": 422, "message": f"Gagal proses file biner: {str(e)}"}

# Jalankan Server
server = SimpleXMLRPCServer(("localhost", 8000))
server.register_instance(TraditionalRPCServer())
print("Server Traditional RPC berjalan di port 8000...")
server.serve_forever()