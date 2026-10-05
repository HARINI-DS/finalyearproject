#!/usr/bin/env python3
import requests

BASE_URL = 'http://127.0.0.1:8000/api'

# Plan
response = requests.post(
    f'{BASE_URL}/workflow/plan',
    json={'goal': 'Create a folder called AION_Test in Downloads'},
)
plan = response.json()
wf_id = plan['workflow_id']
print(f'Plan ID: {wf_id}')

# Approve
response = requests.post(
    f'{BASE_URL}/workflow/approve',
    json={'workflow_id': wf_id, 'approved': True},
)
print(f'Approve status: {response.status_code}')

# Execute
response = requests.post(
    f'{BASE_URL}/workflow/execute',
    json={'workflow_id': wf_id},
)
print(f'Execute status: {response.status_code}')
print(f'Response: {response.text}')
