# 🧭 Master Architect – Minimal App Deployment Runbook

**Purpose:**  
This document outlines the full setup, build, and troubleshooting steps to deploy the **Master Architect Minimal App** — consisting of `api`, `ui`, `worker`, `pgvector`, `redis`, and `ollama` services — on an EC2 instance using Docker Compose.

---

## ⚙️ 1. EC2 System Setup

### 1.1 Update and install dependencies
```bash
sudo dnf update -y
sudo dnf install -y docker docker-compose-plugin socat jq
```

### 1.2 Enable and start Docker
```bash
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
newgrp docker
docker compose version
```

*(If needed, manually install compose plugin)*  
```bash
sudo mkdir -p /usr/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 \
  -o /usr/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/lib/docker/cli-plugins/docker-compose
docker compose version
```

---

## 💾 2. Optional: Move Docker Data to Larger Volume

If `/var/lib/docker` runs out of space, move it to `/data` (EBS volume):

```bash
sudo mkfs -t ext4 /dev/xvdf
sudo mkdir /data
sudo mount /dev/xvdf /data
sudo rsync -aP /var/lib/docker/ /data/docker/
sudo mv /var/lib/docker /var/lib/docker.bak
sudo ln -s /data/docker /var/lib/docker
sudo systemctl restart docker
docker info | grep "Docker Root Dir"
sudo rm -rf /var/lib/docker.bak
```

---

## 🧱 3. Application Build & Directory Layout

```
/application
 ├── ma-min-app/
 │    ├── docker/
 │    │    ├── api.Dockerfile
 │    │    ├── ui.Dockerfile
 │    │    └── worker.Dockerfile
 │    ├── src/
 │    │    ├── ma_app/
 │    │    │   └── api.py
 │    │    └── ui/
 │    │        └── app.py
 │    └── pyproject.toml
 └── RUNBOOK.md
```

---

## 🐳 4. Build Local Images

From `/application`:
```bash
docker build -t ma-api:latest -f ./ma-min-app/docker/api.Dockerfile .
docker build -t ma-worker:latest -f ./ma-min-app/docker/worker.Dockerfile .
docker build -t ma-ui:latest -f ./ma-min-app/docker/ui.Dockerfile .
```

Verify:
```bash
docker images | grep ma-
```

---

## 🧩 5. Docker Compose Setup

### 5.1 Compose directory
```bash
sudo mkdir -p /opt/ma
sudo vi /opt/ma/docker-compose.yml
```

Include services:
- `api` (FastAPI + Uvicorn)
- `worker` (RQ worker)
- `ui` (Streamlit frontend)
- `ollama` (local LLM runtime)
- `pgvector` (Postgres)
- `redis` (queue/cache)

Each service shares a Docker network.

Example snippet:
```yaml
services:
  api:
    image: ma-api:latest
    container_name: ma-api
    depends_on: [pgvector, redis, ollama]
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"

  ui:
    image: ma-ui:latest
    container_name: ma-ui
    depends_on: [api]
    environment:
      API_URL: http://ma-api:8000
    ports:
      - "8501:8501"

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
    entrypoint: ["/bin/sh","-lc","ollama serve & sleep 3 && ollama pull llama3.1:8b && wait"]
```

### 5.2 Bring up the stack
```bash
cd /opt/ma
docker compose up -d
docker compose ps
```

---

## 🔑 6. Environment Variables

### 6.1 Set OpenAI Key
```bash
export OPENAI_API_KEY="sk-..."
echo "OPENAI_API_KEY=$OPENAI_API_KEY" > /application/ma-min-app/.env
```

### 6.2 Verify inside container
```bash
docker compose exec api env | grep OPENAI
```

---

## 🚀 7. API Development & Debugging

### 7.1 Common fixes applied
✅ Added `app = FastAPI()` in `ma_app/api.py`  
✅ Added `/health` and `/generate` routes  
✅ Used `requests` for Ollama calls  
✅ Set `OLLAMA_URL = "http://ollama:11434/api/generate"`  
✅ Disabled Chroma telemetry noise  
✅ Added `requests` to dependencies (`poetry add requests`)

### 7.2 Test health
```bash
curl -s http://localhost:8000/health
# → {"status":"ok"}
```

### 7.3 Test generate
```bash
curl -s http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"hello"}'
```

### 7.4 Example Ollama call
```bash
docker exec ma-api curl -s -H 'Content-Type: application/json' \
  -d '{"model":"llama3.1:8b","prompt":"hello","stream":false}' \
  http://ollama:11434/api/generate | jq .
```

---

## 🖥️ 8. Streamlit UI

### 8.1 Updated `app.py`
- Default `API_URL` → `http://ma-api:8000`
- Handles missing sections gracefully (no tab crash)
- Displays raw `output` field from API

### 8.2 Build & restart
```bash
cd /application
docker build -t ma-ui:latest -f ./ma-min-app/docker/ui.Dockerfile .
docker compose -f /opt/ma/docker-compose.yml up -d
```

### 8.3 Verify
Open in browser:
```
http://<EC2_PUBLIC_IP>:8501
```
Click **API Health Check** → ✅ `{"status":"ok"}`  
Click **Generate** → Model response displayed.

---

## 🔍 9. Validation Checklist

| Check | Command | Expected Result |
|-------|----------|-----------------|
| API Health | `curl http://localhost:8000/health` | `{"status":"ok"}` |
| Generate | `curl -s -X POST http://localhost:8000/generate -d '{"prompt":"hello"}' -H 'Content-Type: application/json'` | Model text |
| UI Health | Click “API Health Check” | `status: ok` |
| Ollama Models | `docker exec ollama ollama list` | lists llama3.1:8b |
| Env Vars | `docker compose exec api env | grep OPENAI` | shows key |
| Logs | `docker logs ma-api --tail=100` | no errors |

---

## 🧰 10. Troubleshooting Reference

| Symptom | Root Cause | Fix |
|----------|-------------|-----|
| `no configuration file provided: not found` | Ran `docker compose` outside compose dir | Run from `/opt/ma` or use `-f /opt/ma/docker-compose.yml` |
| `Please provide an OpenAI API key` | Env not passed | Add to `.env` and `environment:` block |
| 422 “Field required” | Sent `query` instead of `prompt` | Use `{"prompt":"..."}` or normalize |
| `APIStatusError.__init__()` | Old OpenAI call mixed with new SDK | Catch exceptions, don’t instantiate manually |
| 429 insufficient_quota | Key exhausted | Add billing or use Ollama fallback |
| `Attribute 'app' not found` | Missing `app = FastAPI()` | Define it in `ma_app/api.py` |
| `StreamlitAPIException: tabs must contain labels` | No `sections` key in API response | Added fallback to show `output` instead |

---

## ✅ 11. Success Criteria

- All containers running:  
  `docker compose ps` → every service `Up`
- API responds:  
  `curl http://localhost:8000/health` → `{"status":"ok"}`
- `/generate` returns text
- Streamlit UI shows model output without crash

---

## 🧩 12. Next Enhancements (optional)

- Add `/ready` endpoint that checks DB/Redis/Ollama/OpenAI connectivity.  
- Add healthchecks in `docker-compose.yml`:
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-sf", "http://localhost:8000/health"]
    interval: 15s
    timeout: 3s
    retries: 5
  ```
- Add logging & metrics to track latency and request volume.
- Integrate OpenAI + Ollama hybrid fallback for quota resiliency.

---

**End of RUNBOOK.md** ✅
