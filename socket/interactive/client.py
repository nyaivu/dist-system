import xmlrpc.client
import base64
import auth_helper

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

# A. Simulasi Dapatkan Token
token = auth_helper.generate_token()
print(f"Token didapat: {token[:20]}...\n")

# B. Panggil Counter
print("--- Test Counter ---")
response = proxy.call_function(token, "increment")
print(f"Response: {response}\n")

# C. Panggil Upload Gambar
print("--- Test Upload Gambar ---")
try:
    with open("test_image.jpg", "rb") as f: # Pastikan ada file ini
        encoded_img = base64.b64encode(f.read()).decode('utf-8')
    
    response_img = proxy.call_function(token, "upload_image", encoded_img)
    print(f"Metadata: {response_img}")
except FileNotFoundError:
    print("Error: File test_image.png tidak ditemukan untuk testing.")

# D. Test Error Handling (Token Salah)
print("\n--- Test Token Invalid ---")
print(proxy.call_function("token_salah", "increment"))