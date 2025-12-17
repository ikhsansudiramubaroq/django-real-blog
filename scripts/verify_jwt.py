"""
scripts/verify_jwt.py - Script untuk testing JWT Authentication

Cara penggunaan:
    cd c:/python_app/blogapp
    myvenv/Scripts/activate
    python scripts/verify_jwt.py

Script ini akan:
1. Meminta email dan password (gunakan akun yang sudah terdaftar)
2. Mendapatkan access token dan refresh token
3. Test verifikasi token dengan endpoint /token/verify/
4. Test akses ke protected endpoints
"""
import os
import django
import requests
import sys
import getpass

# Setup Django Environment
sys.path.append('c:/python_app/blogapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

BASE_URL = 'http://127.0.0.1:8000'


def get_credentials():
    """Minta email dan password dari user yang sudah terdaftar."""
    print("\n" + "="*50)
    print("JWT Authentication Test")
    print("="*50)
    print("\nMasukkan kredensial akun yang sudah terdaftar:")
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    return email, password


def obtain_tokens(email, password):
    """Dapatkan access token dan refresh token."""
    print("\n--- Obtaining JWT Tokens ---")
    
    token_url = f"{BASE_URL}/author/api/token/"
    payload = {'email': email, 'password': password}
    
    try:
        response = requests.post(token_url, json=payload)
        if response.status_code == 200:
            print("[PASS] Login berhasil! Token didapatkan.")
            tokens = response.json()
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
            print(f"  Access Token (truncated): {access_token[:30]}...")
            print(f"  Refresh Token (truncated): {refresh_token[:30]}...")
            return access_token, refresh_token
        else:
            print("[FAIL] Login gagal!")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"[ERROR] Koneksi gagal: {e}")
        return None, None


def verify_token(token):
    """
    Verifikasi apakah token masih valid.
    Endpoint: POST /author/api/token/verify/
    """
    print("\n--- Verifying Token ---")
    
    verify_url = f"{BASE_URL}/author/api/token/verify/"
    payload = {'token': token}
    
    try:
        response = requests.post(verify_url, json=payload)
        if response.status_code == 200:
            print("[PASS] Token VALID!")
            return True
        else:
            print("[FAIL] Token INVALID atau EXPIRED!")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Koneksi gagal: {e}")
        return False


def refresh_access_token(refresh_token):
    """
    Gunakan refresh token untuk mendapatkan access token baru.
    Endpoint: POST /author/api/token/refresh/
    """
    print("\n--- Refreshing Access Token ---")
    
    refresh_url = f"{BASE_URL}/author/api/token/refresh/"
    payload = {'refresh': refresh_token}
    
    try:
        response = requests.post(refresh_url, json=payload)
        if response.status_code == 200:
            print("[PASS] Access token berhasil di-refresh!")
            tokens = response.json()
            new_access_token = tokens.get('access')
            print(f"  New Access Token (truncated): {new_access_token[:30]}...")
            return new_access_token
        else:
            print("[FAIL] Refresh token failed!")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Koneksi gagal: {e}")
        return None


def test_protected_endpoint(access_token):
    """Test akses ke protected endpoint."""
    print("\n--- Testing Protected Endpoint (List Posts) ---")
    
    if not access_token:
        print("[SKIP] Tidak ada access token")
        return
    
    posts_url = f"{BASE_URL}/author/api/posts/"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(posts_url, headers=headers)
        if response.status_code == 200:
            print("[PASS] API Access berhasil!")
            data = response.json()
            print(f"  Jumlah posts: {len(data)}")
        elif response.status_code == 401:
            print("[FAIL] Unauthorized - Token invalid?")
        elif response.status_code == 403:
            print("[FAIL] Forbidden - User bukan author?")
        else:
            print(f"[FAIL] Status tidak diharapkan: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Koneksi gagal: {e}")


def test_dashboard_endpoint(access_token):
    """Test akses ke dashboard endpoint."""
    print("\n--- Testing Dashboard Endpoint ---")
    
    if not access_token:
        print("[SKIP] Tidak ada access token")
        return
    
    dashboard_url = f"{BASE_URL}/author/api/dashboard/"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(dashboard_url, headers=headers)
        if response.status_code == 200:
            print("[PASS] Dashboard berhasil diakses!")
            data = response.json()
            print(f"  Stats: {data.get('stats', {})}")
        else:
            print(f"[FAIL] Dashboard gagal: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Koneksi gagal: {e}")


def main():
    # Get credentials from user
    email, password = get_credentials()
    
    # Step 1: Obtain tokens
    access_token, refresh_token = obtain_tokens(email, password)
    if not access_token:
        print("\nGagal mendapatkan token. Pastikan email dan password benar.")
        return
    
    # Step 2: Verify access token
    verify_token(access_token)
    
    # Step 3: Verify refresh token
    print("\n--- Verifying Refresh Token ---")
    if verify_token(refresh_token):
        print("  Refresh token masih valid.")
    
    # Step 4: Test protected endpoints
    test_protected_endpoint(access_token)
    test_dashboard_endpoint(access_token)
    
    # Step 5: Demonstrate token refresh
    print("\n" + "="*50)
    print("Demo: Refresh Access Token")
    print("="*50)
    new_access_token = refresh_access_token(refresh_token)
    if new_access_token:
        verify_token(new_access_token)
    
    print("\n" + "="*50)
    print("RINGKASAN JWT ENDPOINTS:")
    print("="*50)
    print(f"""
    1. Obtain Token (Login):
       POST {BASE_URL}/author/api/token/
       Body: {{"email": "your@email.com", "password": "yourpassword"}}
       
    2. Verify Token:
       POST {BASE_URL}/author/api/token/verify/
       Body: {{"token": "your_access_or_refresh_token"}}
       
    3. Refresh Token:
       POST {BASE_URL}/author/api/token/refresh/
       Body: {{"refresh": "your_refresh_token"}}
    """)


if __name__ == '__main__':
    main()
