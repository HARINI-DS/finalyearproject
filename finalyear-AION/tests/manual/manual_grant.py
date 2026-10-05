import requests
response = requests.post(
    "http://127.0.0.1:8000/api/permissions/grant",
    json={"capability": "file_access", "scopes": ["C:\\Users\\jayas\\Downloads"]}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
