import sys
import os
import time
import socket
import subprocess
import logging
from typing import Dict, Any, Optional
import httpx
from app.execution.workspace import ProjectWorkspace

logger = logging.getLogger("forgeswarm.deployment")

class DeploymentManager:
    _running_processes: Dict[str, subprocess.Popen] = {}
    _running_ports: Dict[str, int] = {}

    @classmethod
    def get_free_port(cls, default_port: int = 8010) -> int:
        for port in range(default_port, default_port + 150):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", port))
                    return port
            except OSError:
                continue
        return default_port

    @classmethod
    def ensure_running(cls, project_id: str) -> Optional[int]:
        """
        Guarantees that the staging process for project_id is alive and healthy.
        If it terminated or the host container restarted, automatically relaunches it.
        Returns the active internal port on 127.0.0.1.
        """
        if project_id in cls._running_processes and project_id in cls._running_ports:
            proc = cls._running_processes[project_id]
            port = cls._running_ports[project_id]
            if proc.poll() is None:
                # Fast liveness probe
                try:
                    with httpx.Client(timeout=1.0) as client:
                        resp = client.get(f"http://127.0.0.1:{port}/health")
                        if resp.status_code == 200:
                            return port
                except Exception:
                    pass

        # Needs start or restart
        ws = ProjectWorkspace(project_id)
        if not (ws.root_path / "app" / "main.py").exists():
            logger.warning(f"Project {project_id} does not have app/main.py; cannot start staging.")
            return None

        logger.info(f"Auto-spawning staging server for project {project_id}...")
        res = cls.deploy_staging(project_id, ws)
        if res.get("status") == "HEALTHY":
            return res.get("port")
        return None

    @classmethod
    def deploy_staging(cls, project_id: str, workspace: ProjectWorkspace) -> Dict[str, Any]:
        """
        Deploys the generated project to an isolated local execution sandbox.
        Validates deployment via automated health check probes and smoke testing.
        Exposes the app publicly via ForgeSwarm's unified reverse proxy route: /api/projects/{project_id}/app/
        """
        # Stop any existing process for this project
        cls.stop_deployment(project_id)

        port = cls.get_free_port(8010)
        workspace_dir = str(workspace.root_path.resolve())
        log_file_path = workspace.root_path / "staging_server.log"
        log_f = open(log_file_path, "w", encoding="utf-8")

        env = os.environ.copy()
        env["PYTHONPATH"] = workspace_dir

        # Launch generated FastAPI server in detached subprocess
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=workspace_dir,
            stdout=log_f,
            stderr=log_f,
            env=env,
            text=True
        )
        cls._running_processes[project_id] = proc
        cls._running_ports[project_id] = port

        # Internal health check polling
        target_url = f"http://127.0.0.1:{port}"
        health_url = f"{target_url}/health"
        is_healthy = False
        health_data = {}

        for attempt in range(16):
            time.sleep(0.5)
            # Check if process died
            if proc.poll() is not None:
                log_f.flush()
                err_text = log_file_path.read_text(encoding="utf-8", errors="ignore") if log_file_path.exists() else "No logs"
                logger.error(f"Staging process terminated early: {err_text}")
                return {
                    "status": "FAILED",
                    "app_url": None,
                    "port": port,
                    "health_check_status": "FAIL",
                    "smoke_tests_passed": False,
                    "logs": f"Server failed to start:\n{err_text}"
                }
            try:
                with httpx.Client(timeout=2.0) as client:
                    resp = client.get(health_url)
                    if resp.status_code == 200:
                        is_healthy = True
                        health_data = resp.json()
                        break
            except Exception:
                continue

        if not is_healthy:
            cls.stop_deployment(project_id)
            return {
                "status": "FAILED",
                "app_url": None,
                "port": port,
                "health_check_status": "FAIL",
                "smoke_tests_passed": False,
                "logs": "Health check timed out after 8 seconds."
            }

        # Run Smoke Tests against the live running instance
        smoke_passed = False
        try:
            with httpx.Client(timeout=3.0) as client:
                h_resp = client.get(health_url)
                o_resp = client.get(f"{target_url}/openapi.json")
                if h_resp.status_code == 200 and o_resp.status_code == 200:
                    smoke_passed = True
        except Exception as e:
            logger.error(f"Smoke test failed: {e}")

        if not smoke_passed:
            cls.rollback(project_id)
            return {
                "status": "ROLLED_BACK",
                "app_url": None,
                "port": port,
                "health_check_status": "PASS",
                "smoke_tests_passed": False,
                "logs": "Smoke test failed: Server endpoints did not respond as expected. Deployment rolled back."
            }

        # The public unified URL routes via ForgeSwarm's secure proxy
        public_url = f"/api/projects/{project_id}/app/"

        return {
            "status": "HEALTHY",
            "app_url": public_url,
            "internal_url": target_url,
            "port": port,
            "health_check_status": "PASS",
            "smoke_tests_passed": True,
            "logs": f"Staging server successfully deployed on {public_url} (internal sandbox port {port}). Health check and smoke tests PASSED."
        }

    @classmethod
    def stop_deployment(cls, project_id: str):
        if project_id in cls._running_processes:
            proc = cls._running_processes[project_id]
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            del cls._running_processes[project_id]
        
        if project_id in cls._running_ports:
            del cls._running_ports[project_id]

    @classmethod
    def rollback(cls, project_id: str):
        cls.stop_deployment(project_id)
