# Azure Deployment Guide

---

## Prerequisites

- Azure subscription with quota for GPU VMs (NC-series)
- Azure CLI installed: `winget install Microsoft.AzureCLI`
- Docker installed locally (to push the image)

---

## Resource Group Structure

Recommended naming convention for a team/project:

```
Subscription
└── Resource Group: rg-transcription-prod
    ├── Container Registry: crtranscription
    ├── VM or Container Instance (GPU)
    ├── Storage Account: sttranscription
    │   ├── Container: models      ← cached Whisper models
    │   ├── Container: input       ← audio/video uploads
    │   └── Container: output      ← transcription results
    └── Key Vault: kv-transcription ← secrets (.env values)
```

Login and set your subscription:

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
az group create --name rg-transcription-prod --location westeurope
```

---

## Option A — Azure VM with GPU (recommended for daily use)

Best for: teams that process audio daily at fixed hours. Pay only when the VM is running.

### 1. Create the VM

```bash
az vm create \
  --resource-group rg-transcription-prod \
  --name vm-transcription \
  --image Ubuntu2204 \
  --size Standard_NC4as_T4_v3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard
```

> **Standard_NC4as_T4_v3** → T4 GPU (16 GB VRAM), 4 vCPUs, ~$0.50/h in westeurope.
> `large-v3` runs comfortably here. `medium` is around 8–10x real-time.

### 2. Open port 8000

```bash
az vm open-port --resource-group rg-transcription-prod --name vm-transcription --port 8000
```

### 3. Install NVIDIA drivers + Docker on the VM

```bash
ssh azureuser@<VM_PUBLIC_IP>

# NVIDIA drivers
sudo apt-get update
sudo apt-get install -y ubuntu-drivers-common
sudo ubuntu-drivers install

# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 4. Push your Docker image to Azure Container Registry

```bash
# Create registry (one time)
az acr create \
  --resource-group rg-transcription-prod \
  --name crtranscription \
  --sku Basic

# Login and push
az acr login --name crtranscription
docker build -t crtranscription.azurecr.io/transcription-service:latest .
docker push crtranscription.azurecr.io/transcription-service:latest
```

### 5. Run on the VM

```bash
# On the VM
docker pull crtranscription.azurecr.io/transcription-service:latest

docker run -d \
  --name transcription \
  --gpus all \
  -p 8000:8000 \
  --env-file /home/azureuser/.env \
  -v /mnt/models:/app/models \
  -v /mnt/input:/app/input \
  -v /mnt/output:/app/output \
  crtranscription.azurecr.io/transcription-service:latest
```

---

## Option B — Azure Container Instances (ACI)

Best for: sporadic, on-demand workloads. No VM to manage. Start a container, process, stop.

```bash
az container create \
  --resource-group rg-transcription-prod \
  --name aci-transcription \
  --image crtranscription.azurecr.io/transcription-service:latest \
  --registry-login-server crtranscription.azurecr.io \
  --registry-username $(az acr credential show --name crtranscription --query username -o tsv) \
  --registry-password $(az acr credential show --name crtranscription --query passwords[0].value -o tsv) \
  --cpu 4 \
  --memory 8 \
  --gpu-count 1 \
  --gpu-sku K80 \
  --ports 8000 \
  --environment-variables \
      WHISPER_MODEL=large-v3 \
      WHISPER_DEVICE=gpu \
      WHISPER_BEAM_SIZE=5 \
      WHISPER_VAD_FILTER=true \
      OUTPUT_DIR=/app/output
```

> ACI GPU availability varies by region. `K80` is most available; `V100` in some regions.
> Cost: ~$1.20/h for K80 — only pay while the container is running.

Stop when done:
```bash
az container stop --resource-group rg-transcription-prod --name aci-transcription
az container start --resource-group rg-transcription-prod --name aci-transcription
```

---

## "Only up at certain times" — Auto Start/Stop

### VM schedule via Azure Automation (no code needed)

In the Azure Portal:
1. Go to your VM → **Auto-shutdown** → enable, set time (e.g. 20:00)
2. For auto-start, create an **Azure Automation Account** with a runbook:

```powershell
# Runbook: Start VM at 08:00
Connect-AzAccount -Identity
Start-AzVM -ResourceGroupName "rg-transcription-prod" -Name "vm-transcription"
```

Schedule the runbook as a recurring job (Mon–Fri, 08:00).

### Via Azure CLI (manual control)

```bash
# Start the VM (morning)
az vm start --resource-group rg-transcription-prod --name vm-transcription

# Stop + deallocate (evening — stops billing)
az vm deallocate --resource-group rg-transcription-prod --name vm-transcription
```

> **Important**: use `deallocate`, not just `stop`. A stopped VM still bills for compute.

### Cost example

| Schedule | Hours/month | Monthly cost (NC4as T4) |
|---|---|---|
| 24/7 | 730h | ~$365 |
| Mon–Fri 08–20 | 240h | ~$120 |
| On demand only | ~40h | ~$20 |

---

## What the App Needs to Run in Azure

### `.env` on the VM (no CUDA_BIN_PATH needed — Linux has it in PATH)

```env
WHISPER_MODEL=large-v3
WHISPER_DEVICE=gpu
OUTPUT_DIR=/app/output
WHISPER_BEAM_SIZE=5
WHISPER_VAD_FILTER=true
WHISPER_CONDITION_ON_PREVIOUS_TEXT=true
```

### Model caching (avoid re-downloading on each start)

Mount a persistent volume or Azure File Share for `/app/models`:

```bash
# Azure File Share
az storage share create --name whisper-models --account-name sttranscription

# Mount on VM at startup
sudo mount -t cifs //sttranscription.file.core.windows.net/whisper-models /mnt/models \
  -o username=sttranscription,password=<KEY>,dir_mode=0777,file_mode=0777
```

Once the model is downloaded once, it persists across VM restarts.

### Health check

The app already exposes `GET /health`. Azure Load Balancer or Application Gateway can use this endpoint to verify the service is ready before routing traffic.

---

## Secrets — Key Vault integration

Instead of an `.env` file on the VM, use Key Vault:

```bash
az keyvault create --name kv-transcription --resource-group rg-transcription-prod
az keyvault secret set --vault-name kv-transcription --name WHISPER-MODEL --value "large-v3"
az keyvault secret set --vault-name kv-transcription --name API-KEY --value "your-api-key"
```

Assign the VM's managed identity read access to the vault — no secrets on disk.

---

## Summary — Which option to pick

| Scenario | Recommendation |
|---|---|
| Daily HR processing, fixed hours | VM NC4as T4 + auto start/stop |
| Occasional batch jobs | ACI on demand |
| High volume, team usage | AKS with GPU node pool |
| Testing / low budget | VM + manual start/stop via CLI |
