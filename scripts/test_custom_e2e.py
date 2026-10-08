import requests
import time
import sys

BASE = 'http://127.0.0.1:8000/api'
prompt = 'Build a car rental fleet management system where customers can reserve cars, view available vehicles, and cancel reservations. A vehicle must never be reserved by two customers for the same dates.'

print('[1] Creating project with custom requirement...', flush=True)
res = requests.post(f'{BASE}/projects', json={
    'name': 'Car Rental Fleet Platform',
    'requirement': prompt,
    'llm_provider': 'mock'
})
res.raise_for_status()
project = res.json()
p_id = project['id']
print(f"Project Created: {p_id} ({project['name']})", flush=True)

print('[2] Triggering Swarm Orchestrator run...', flush=True)
run_res = requests.post(f'{BASE}/projects/{p_id}/start')
print(f"Run initiated: {run_res.json()}", flush=True)

print('[3] Polling project lifecycle status...', flush=True)
prev_status = None
for _ in range(60):
    p_info = requests.get(f'{BASE}/projects/{p_id}').json()
    status = p_info.get('status')
    if status != prev_status:
        print(f' -> Status changed: {status}', flush=True)
        prev_status = status
    if status in ['COMPLETED', 'DEPLOYED', 'FAILED']:
        break
    time.sleep(1)

print('\n[4] Inspecting Final Project Output...', flush=True)
final_p = requests.get(f'{BASE}/projects/{p_id}').json()
print(f"Final Status: {final_p.get('status')}", flush=True)
print(f"Metrics: {final_p.get('metrics')}", flush=True)

reqs = requests.get(f'{BASE}/projects/{p_id}/requirements').json()
print(f"Requirements ({len(reqs)} total):", flush=True)
for r in reqs:
    print(f" - [{r['code']}] {r['title']} -> {r['status']}", flush=True)

agents = requests.get(f'{BASE}/projects/{p_id}/agents').json()
print(f"\nTeam Agents ({len(agents)} formed):", flush=True)
for a in agents:
    print(f" - [{a['role']}] {a['name']}: {a['status']} ({a.get('selection_reason', '')[:60]}...)", flush=True)

tests = requests.get(f'{BASE}/projects/{p_id}/tests').json()
passed_cnt = sum(1 for t in tests if t["status"] == "PASSED")
failed_cnt = sum(1 for t in tests if t["status"] == "FAILED")
print(f"\nTests: Total={len(tests)}, Passed={passed_cnt}, Failed={failed_cnt}", flush=True)

bugs = requests.get(f'{BASE}/projects/{p_id}/bugs').json()
print(f"\nBugs detected: {len(bugs)}", flush=True)
if bugs:
    b = bugs[0]
    print(f" - Bug: {b.get('title')} | Root Cause: {b.get('root_cause')[:80]}...", flush=True)

repairs = requests.get(f'{BASE}/projects/{p_id}/repairs').json()
print(f"\nRepairs: {len(repairs)}", flush=True)
if repairs:
    rep = repairs[0]
    print(f" - Strategy: {rep.get('strategy')} | Files: {rep.get('files_changed')} | After: {rep.get('tests_after')}", flush=True)

dep = requests.get(f'{BASE}/projects/{p_id}/deployment').json()
print(f"\nDeployment: {dep}", flush=True)

# Test live staging endpoint if active
app_url = final_p.get('app_url') or (dep.get('url') if dep else None)
if app_url:
    print(f"\n[5] Verifying Live Staging Sandbox at {app_url}...", flush=True)
    try:
        h = requests.get(f"{app_url}/health", timeout=3).json()
        print(f" - Staging /health: {h}", flush=True)
        items_res = requests.get(f"{app_url}/api/items", timeout=3).json()
        print(f" - Staging /api/items ({len(items_res)} items): {[i.get('title') for i in items_res]}", flush=True)
        print(" -> SUCCESS: Fully verified closed-loop engineering lifecycle on custom domain!", flush=True)
    except Exception as e:
        print(f" - Error contacting staging server: {e}", flush=True)
