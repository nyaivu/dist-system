import xmlrpc.client
import auth_helper

def run_xml_rpc():
    proxy = xmlrpc.client.ServerProxy("http://localhost:9000/")
    token = auth_helper.generate_token()

    print("--- Testing XML-RPC Counter ---")
    res_counter = proxy.execute_action(token, "get_counter")
    print(f"Response: {res_counter}")

    print("\n--- Testing XML-RPC File Upload ---")
    try:
        with open("./test_image.jpg", "rb") as f:
            # WAJIB: Bungkus biner ke dalam objek Binary
            binary_data = xmlrpc.client.Binary(f.read())
            
        res_upload = proxy.execute_action(token, "upload", binary_data)
        if res_upload["status"] == "success":
            print(f"Metadata: {res_upload['metadata']}")
        else:
            print(f"Error: {res_upload['message']}")
    except FileNotFoundError:
        print("File gambar tidak ditemukan.")

    print("\n--- Testing Invalid Token ---")
    print(proxy.execute_action("token-salah", "get_counter"))

if __name__ == "__main__":
    run_xml_rpc()