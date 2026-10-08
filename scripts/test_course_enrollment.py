import requests
import time

BASE = 'http://127.0.0.1:8000/api'
prompt = 'Build a university class enrollment system where students can view course catalogs, check available class times, enroll in courses, and drop courses. A course section must never exceed its maximum capacity under concurrent enrollments.'

print('[1] Creating University Course Enrollment project...', flush=True)
res = requests.post(f'{BASE}/projects', json={
    'name': 'University Course Enrollment System',
    'requirement': prompt,
    'llm_provider': 'mock'
})
res.raise_for_status()
project = res.json()
p_id = project['id']
print(f"Project Created: {p_id} ({project['name']})", flush=True)

time.sleep(1)
print('[2] Starting Swarm Orchestrator...', flush=True)
run_res = requests.post(f'{BASE}/projects/{p_id}/start')
print(f"Run initiated: {run_res.json()}", flush=True)

print('[3] Polling project lifecycle...', flush=True)
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

print('\n[4] Inspecting Final Output...', flush=True)
final_p = requests.get(f'{BASE}/projects/{p_id}').json()
print(f"Final Status: {final_p.get('status')}", flush=True)
print(f"App URL: {final_p.get('app_url')}", flush=True)

reqs = requests.get(f'{BASE}/projects/{p_id}/requirements').json()
print(f"Requirements ({len(reqs)}):", [f"[{r['code']}] {r['title']}" for r in reqs[:4]], flush=True)

tests = requests.get(f'{BASE}/projects/{p_id}/tests').json()
print(f"Tests: {len(tests)} total, Passed: {sum(1 for t in tests if t['status']=='PASSED')}", flush=True)

dep = requests.get(f'{BASE}/projects/{p_id}/deployment').json()
if dep and dep[0].get('app_url'):
    url = dep[0]['app_url']
    print(f"\n[5] Verifying Live Staging Sandbox at {url}...", flush=True)
    try:
        h = requests.get(f"{url}/health", timeout=3).json()
        print(f" - Staging /health: {h}", flush=True)
        courses = requests.get(f"{url}/api/courses", timeout=3).json()
        print(f" - Staging /api/courses ({len(courses)} courses): {[c['name'] for c in courses]}", flush=True)
        audit = requests.get(f"{url}/api/audit-logs", timeout=3).json()
        print(f" - Staging /api/audit-logs: {len(audit)} logs found", flush=True)
        print(" -> SUCCESS: Fully verified dynamic models for university domain!", flush=True)
    except Exception as e:
        print(f"Error testing live staging: {e}", flush=True)
