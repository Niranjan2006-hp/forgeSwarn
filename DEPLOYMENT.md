# 🌐 ForgeSwarm — Real-World Production Deployment Guide

ForgeSwarm can be deployed for the real world across multiple environments:
1. **Live Instant Public Tunnel** (Access the running swarm from anywhere on the internet right now)
2. **One-Click Cloud PaaS Deployment** (Render.com, Railway, Fly.io)
3. **Containerized Production VPS** (Docker Compose with Nginx & PostgreSQL on AWS, GCP, DigitalOcean, Hetzner)

---

## 🚀 1. Live Instant Public Access (Running Right Now)

Your active local instance has been exposed to the public internet via a secure gateway tunnel:

- **Public Dashboard URL**: `https://itchy-turkeys-walk.loca.lt`
- **Tunnel Password / IP**: `157.50.200.227` *(Enter this if prompted on first browser visit)*
- **Local Network Access**: `http://10.129.70.149:5173`
- **Local Machine Access**: `http://localhost:5173`

---

## ☁️ 2. Deploy to Render.com (Recommended Free/Low-Cost Cloud)

The repository includes a ready-to-use [`render.yaml`](./render.yaml) blueprint:

1. Push this repository to **GitHub** or **GitLab**.
2. Go to [dashboard.render.com](https://dashboard.render.com/) and click **New > Blueprint**.
3. Connect your repository. Render automatically reads `render.yaml` and provisions:
   - **`forgeswarm-api`**: FastAPI Swarm Engine (Python Web Service)
   - **`forgeswarm-ui`**: Cyberpunk React Dashboard (Static Site)
4. (Optional) Set your API Keys under Environment Variables:
   - `GEMINI_API_KEY` (or `OPENAI_API_KEY`)
5. Click **Apply** to deploy.

---

## 🐳 3. Deploy with Docker Compose (Any Cloud VPS)

You can run ForgeSwarm in production on any Linux virtual machine (AWS EC2, GCP Compute Engine, DigitalOcean Droplet, Linode):

### Prerequisites
- Docker & Docker Compose installed on the host.

### Deployment Command
```bash
# Clone the repository
git clone <your-repo-url>
cd forgeswarm

# Launch all production containers (Backend, Frontend Nginx, PostgreSQL)
docker-compose up -d --build
```

### Services Started:
- **Frontend (Nginx)**: Port `5173` (or reverse-proxied to `80/443`)
- **Backend (FastAPI)**: Port `8002`
- **Database (PostgreSQL)**: Port `5432`

---

## 🪂 4. Deploy to Fly.io

The repository includes [`fly.toml`](./fly.toml):

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy backend
fly launch
fly deploy
```

---

## 🔑 Production Environment Variables Reference

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Production mode toggle |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8002` | Backend service port |
| `DATABASE_URL` | `sqlite:///forgeswarm.db` | Database connection string (PostgreSQL supported) |
| `DEFAULT_LLM_PROVIDER` | `mock` | `mock`, `gemini`, or `openai` |
| `GEMINI_API_KEY` | - | Google Gemini API Key |
| `OPENAI_API_KEY` | - | OpenAI API Key |
| `WORKSPACE_ROOT` | `/app/generated_projects` | File storage path for generated software |
