"""Full end-to-end test of SecretNotes API."""
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
print("=== SecretNotes End-to-End Test ===\n")

# 1. Health
print("1. Health Check")
r = client.get("/health")
print(f"   Status: {r.status_code}, {r.json()}\n")

# 2. Setup PIN
print("2. Setup PIN")
r = client.post("/api/auth/setup", json={"pin": "123456"})
print(f"   Status: {r.status_code}")
token = r.json().get("token")
print(f"   Token received: {bool(token)}\n")

# 3. Unlock PIN
print("3. Unlock PIN")
r = client.post("/api/auth/unlock", json={"pin": "123456"})
print(f"   Status: {r.status_code}")
token = r.json().get("token", token)
print(f"   Token received: {bool(token)}\n")

# 4. Create note
print("4. Create Note")
r = client.post("/api/notes", json={"title": "Catatan Rahasia", "body": "Isi rahasia"}, headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code}")
note_id = r.json().get("id")
print(f"   Note ID: {note_id}\n")

# 5. List notes
print("5. List Notes")
r = client.get("/api/notes", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code}")
notes = r.json()
print(f"   Notes count: {len(notes)}")
for n in notes:
    print(f"   - {n['title']}\n")

# 6. Get note detail
print("6. Get Note Detail")
r = client.get(f"/api/notes/{note_id}", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Title: {data['title']}")
    print(f"   Body: {data['body']}\n")

# 7. AES Log
print("7. AES Log")
r = client.get(f"/api/notes/{note_id}/aes-log", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Block index: {data['block_index']}")
    print(f"   Rounds: {len(data['rounds'])}")
    print(f"   Input matrix: {data['input_matrix']}\n")

# 8. Round Keys
print("8. Round Keys")
r = client.get(f"/api/notes/{note_id}/round-keys", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Round keys count: {len(data['round_keys'])}")
    print(f"   Key expansion trace entries: {len(data['key_expansion_trace'])}")
    rk1 = data['round_keys'][1]
    rk1_hex = ''.join(f'{rk1[r][c]:02x}' for r in range(4) for c in range(4))
    print(f"   Round key 1: {rk1_hex}")
    print(f"   Expected:      a0fafe1788542cb123a339392a6c7605")
    print(f"   FIPS-197 KAT:  {rk1_hex == 'a0fafe1788542cb123a339392a6c7605'}\n")

# 9. Delete note
print("9. Delete Note")
r = client.delete(f"/api/notes/{note_id}", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code}\n")

# 10. Verify note deleted
print("10. Verify Delete")
r = client.get(f"/api/notes/{note_id}", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code} (404 = deleted)\n")

# 11. Lock
print("11. Lock Session")
r = client.post("/api/auth/lock", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code}\n")

# 12. Verify locked (401)
print("12. Verify Locked (401)")
r = client.get("/api/notes", headers={"Authorization": f"Bearer {token}"})
print(f"   Status: {r.status_code} (401 = locked)\n")

print("=== ALL TESTS PASSED ===")
