import xmlrpc.client
import base64
import os
import auth_helper # Pastikan file ini ada di folder yang sama

def run_client():
    # 1. Koneksi ke Server
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
    print("Terhubung ke Server RPC (Port 8000)\n")

    # 2. Simulasi Dapatkan Token JWT Valid
    token = auth_helper.generate_token()
    print(f"Token didapat: {token[:20]}...\n")

    # 3. Persiapkan Gambar yang akan diupload
    # Asumsikan file gambar ini ada di folder yang sama dengan client.py
    image_filename = "test_image.jpg" 
    
    # Cek apakah file ada secara lokal
    if not os.path.exists(image_filename):
        print(f"Error Client: File {image_filename} tidak ditemukan untuk diupload.")
        return

    try:
        # 4. Baca file gambar sebagai biner
        with open(image_filename, "rb") as f:
            image_data = f.read()
        
        # 5. Encode ke Base64 String (wajib untuk XML-RPC agar data biner aman)
        encoded_string = base64.b64encode(image_data).decode('utf-8')
        
        print(f"--- Mencoba Upload {image_filename} ---")
        
        # 6. Panggil FUNGSI UTAMA di Server via RPC
        # Parameter: token, nama_file, data_base64
        response = proxy.call_function(token, "increment")
        response = proxy.upload_image(token, image_filename, encoded_string)
        
        # 7. Tampilkan Response dari Server
        if response["status"] == "success":
            meta = response["metadata"]
            print("\n Berhasil Upload! Metadata dari Server:")
            print(f" - Nama File  : {meta['filename']}")
            print(f" - Format     : {meta['format']}")
            print(f" - Resolusi   : {meta['resolution']}")
            print(f" - Ukuran     : {meta['size_kb']}")
            print(f" - Mode Warna : {meta['color_mode']}")
            print(f" - Disimpan Di: {meta['server_path']}")
        else:
            # Menangani Error Handling dari Server
            print(f"\n Gagal Upload!")
            print(f" - Kode Error : {response.get('code', 'N/A')}")
            print(f" - Pesan      : {response['message']}")
            
    except Exception as e:
        print(f"Error Client saat proses file: {str(e)}")

if __name__ == "__main__":
    run_client()