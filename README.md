# Getting Started with MCP & A2A with ADK

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg)](https://github.com/google/adk-python)
[![Protocol](https://img.shields.io/badge/Protocol-A2A-34A853.svg)](https://github.com/google-a2a/a2a-python)
[![Protocol](https://img.shields.io/badge/Protocol-MCP-EA4335.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A sample multi-agent system demonstrating **Model Context Protocol (MCP)** and 
**Agent2Agent (A2A)** working together with **Agent Development Kit (ADK)**. 
All services follow ADK Best Practices and can be run completely locally via ADK CLI or fully deployed to Google Cloud Run.

![Architecture Overview](images/architecture.png)

---

## Overview

The sample aims at laying out a clean, production-ready foundation and showcasing the best practices of MCP + A2A + ADK.

### <img height="20" width="20" src="images/mcp-favicon.ico" alt="MCP Logo" /> Model Context Protocol (MCP)

> MCP is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools. - [Anthropic](https://modelcontextprotocol.io/introduction)

The MCP server in this example exposes a tool `get_exchange_rate` that can be used to get the exchange rate between two currencies such as USD and EUR. It leverages the [Frankfurter](https://www.frankfurter.dev/) API to get the currency exchange rate. Our agent uses an MCP client to invoke this tool when needed.

### <img height="20" width="20" src="https://a2a-protocol.org/v0.2.5/assets/a2a-logo-black.svg" alt="A2A Logo" /> Agent2Agent (A2A)

> Agent2Agent (A2A) protocol addresses a critical challenge in the AI landscape: enabling gen AI agents, built on diverse frameworks by different companies running on separate servers, to communicate and collaborate effectively - as agents, not just as tools. A2A aims to provide a common language for agents, fostering a more interconnected, powerful, and innovative AI ecosystem. - [A2A](https://github.com/a2aproject/A2A)

In this sample, agents adhere to the **Separation of Concerns (SoC)** best practice:
- **Pure Agent Definition**: `currency_agent/agent.py` contains only the agent definition (`root_agent = LlmAgent(...)`) without any server or protocol boilerplate.
- **A2A Agent Card Pre-generation**: The Agent Card (`currency_agent/agent.json`) is generated once ahead-of-time using `generate_card.py`.
- **A2A Exposure**: The agent is exposed over A2A seamlessly via ADK's built-in servers (`adk api_server --a2a` or `adk deploy cloud_run --a2a`).
- **Remote Consumption**: `travel_agent` consumes `currency_agent` via `RemoteA2aAgent`.

### <img height="20" width="20" src="images/adk-favicon.ico" alt="ADK Logo" /> Agent Development Kit (ADK)

> ADK is a flexible and modular framework for developing and deploying AI agents. While optimized for Gemini and the Google ecosystem, ADK is model-agnostic, deployment-agnostic, and is built for compatibility with other frameworks. - [ADK](https://github.com/google/adk-python)

ADK is used as the core orchestration framework. It manages agent definitions, executes tool calls (including MCP), serves Web UIs, handles JSON-RPC A2A routing, and provides CLI tools for local development and cloud deployment.

---

## 🏗️ Architecture Overview

The system consists of 1 orchestrating agent with Web UI, 1 remote agent via A2A, 1 local agent tool, and 1 MCP server:

```
+-----------------------------------------------------------------------------------+
|                                  Clients                                          |
|                     ADK Web UI (Browser)  |  HTTP Callers                         |
+------------------------------------------+----------------------------------------+
                                           | (HTTP / Web UI)
                                           v
+-----------------------------------------------------------------------------------+
| travel_agent (Port 8082 / Cloud Run)                                              |
| - Pure ADK Agent served via `adk web` or `adk deploy cloud_run --with_ui`         |
|                                                                                   |
|   +--> [Local AgentTool] weather_agent (travel_agent/subagents/weather_agent.py)  |
|        - Directly wrapped as AgentTool (in-process, zero network hops)            |
|        - Live weather tool via wttr.in API with fallback                          |
|   +--> [Remote AgentTool] currency_agent                                          |
|        - Consumed via RemoteA2aAgent over A2A protocol (JSON-RPC)                 |
+------------------------------------------+----------------------------------------+
                                           | (A2A Protocol / JSON-RPC)
                                           v
+-----------------------------------------------------------------------------------+
| currency_agent (Port 8081 / Cloud Run)                                            |
| - Pure ADK Agent (`currency_agent/agent.py`)                                      |
| - Pre-generated Agent Card (`currency_agent/agent.json`)                          |
| - Exposed via `adk api_server --a2a` or `adk deploy cloud_run --a2a`              |
| - Consumes get_exchange_rate tool via FastMCP Streamable HTTP client              |
+------------------------------------------+----------------------------------------+
                                           | (MCP Streamable HTTP /mcp)
                                           v
+-----------------------------------------------------------------------------------+
| currency_mcp_server (Port 8080 / Cloud Run)                                       |
| - FastMCP server providing real-time exchange rates via Frankfurter API           |
+-----------------------------------------------------------------------------------+
```

### Key Components

- **`currency_mcp_server/`**: A FastMCP server exposing the `get_exchange_rate` tool over Streamable HTTP (`/mcp`), backed by the public [Frankfurter API](https://api.frankfurter.dev/).
- **`currency_agent/`**: 
  - `agent.py`: Pure ADK `LlmAgent` definition. Can be run standalone or exposed via A2A.
  - `generate_card.py`: Script to generate `agent.json` ahead-of-time.
  - `agent.json`: Standard A2A Agent Card used by ADK to mount A2A routes.
- **`travel_agent/`**: A travel assistant ADK agent coordinating between:
  - **`weather_agent`**: A **local agent wrapped as an `AgentTool`**, demonstrating in-process execution.
  - **`currency_agent`**: A **remote agent wrapped as an `AgentTool`**, delegating requests over the A2A protocol.

---

## 📦 Dependency Management (`uv` Workspace)

Project dependencies are organized as a unified **`uv` Workspace**:
- Root `pyproject.toml` orchestrates workspace members (`currency_mcp_server`, `currency_agent`, `travel_agent`).
- Running `uv sync` at the root automatically resolves and installs all packages for local development into a single `.venv`.
- Each service directory has its own self-contained `pyproject.toml` for independent builds and deployments.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation):
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Google Cloud SDK (`gcloud`) if deploying to Cloud Run.

### Installation

1. Clone repository:
   ```bash
   git clone https://github.com/kiwonlee/getting-started-mcp-a2a-adk.git
   cd getting-started-mcp-a2a-adk
   ```

2. Install all dependencies across the workspace:
   ```bash
   uv sync
   ```

3. Configure Environment Variables:
   Create a `.env` file in the project root:
   
   ```sh
   cp .env.example .env
   ```
   
   ```sh
   GOOGLE_GENAI_USE_ENTERPRISE=TRUE
   GOOGLE_CLOUD_PROJECT=<your_gcp_project_id>
   GOOGLE_CLOUD_LOCATION=global
   ```

---

## ☁️ Cloud Run Deployment

All components can be deployed cleanly to Google Cloud Run. You can use ADK's built-in `adk deploy cloud_run` or standard `gcloud run deploy`.

### Environment Setup

Set your Google Cloud project, region, and dedicated service account details:

```bash
export PROJECT_ID=<YOUR_GOOGLE_CLOUD_PROJECT_ID>
export REGION=us-central1
export SA_NAME="getting-started-mcp-a2a-adk"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```

Enable required GCP APIs:

```bash
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       aiplatform.googleapis.com
```

Create a dedicated Service Account for running the MCP server and ADK agents, and grant required permissions:

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# 1. Create dedicated agent runner service account
gcloud iam service-accounts create $SA_NAME \
    --display-name="Getting-started-mcp-a2a-adk Service Account"

# 2. Grant runtime (Vertex AI, Logging) and build permissions to the dedicated SA
for ROLE in \
  roles/aiplatform.user \
  roles/logging.logWriter \
  roles/storage.admin \
  roles/artifactregistry.writer \
  roles/cloudbuild.builds.builder; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:${SA_EMAIL}" \
      --role="$ROLE"
done
```

---

### Step 1: Deploy Currency MCP Server

Deploy the FastMCP server with the dedicated service account:

```bash
gcloud run deploy currency-mcp-server \
  --source currency_mcp_server \
  --region $REGION \
  --service-account $SA_EMAIL \
  --allow-unauthenticated

# Capture deployed MCP server URL
MCP_SERVER_URL=$(gcloud run services describe currency-mcp-server --region $REGION --format='value(status.url)')/mcp
echo "MCP Server URL: $MCP_SERVER_URL"
```

---

### Step 2: Resolve Target URL & Generate Currency Agent Card (`agent.json`)

Before deploying `currency_agent`, generate its A2A Agent Card (`agent.json`).

> [!IMPORTANT]
> **Why `agent.json` must be generated before deployment**:
> 1. **A2A Routes Packaging**: ADK's `adk deploy cloud_run --a2a` bundles `agent.json` into the Docker image. If `agent.json` is missing at build time, the A2A endpoints (`/a2a/currency_agent`) will not be mounted.
> 2. **Reachable RPC Target**: The `supportedInterfaces` in `agent.json` instructs A2A clients where to send RPC calls. It must contain the reachable Cloud Run endpoint (`https://.../a2a/currency_agent`) rather than `localhost`.
> 3. **Deterministic Cloud Run Domain**: Cloud Run services in the same project and region share the exact same domain suffix. We can deterministically predict `currency-agent`'s URL directly from the deployed `currency-mcp-server` without deploying twice!

Resolve the target URL and generate the card:

```bash
# 1. Determine target Currency Agent URL (either from existing service or predicted from MCP server domain)
CURRENCY_AGENT_URL=$(gcloud run services describe currency-agent --region $REGION --format='value(status.url)' 2>/dev/null || echo "")

if [ -z "$CURRENCY_AGENT_URL" ]; then
  DOMAIN_SUFFIX=$(gcloud run services describe currency-mcp-server --region $REGION --format='value(status.url)' | sed 's/.*currency-mcp-server//')
  CURRENCY_AGENT_URL="https://currency-agent${DOMAIN_SUFFIX}"
fi
echo "Target Currency Agent URL: $CURRENCY_AGENT_URL"

# 2. Generate agent.json with MCP tools and the Cloud Run RPC URL
MCP_SERVER_URL="$MCP_SERVER_URL" uv run python -m currency_agent.generate_card --url "${CURRENCY_AGENT_URL}/a2a/currency_agent"
```
```bash
cat ./currency_agent/agent.json
```
---

### Step 3: Deploy Currency Agent (ADK with A2A)

Deploy using ADK's `adk deploy cloud_run` with `--service_name`, `--a2a`, and the `--` separator to pass `gcloud` flags:

```bash
uv run adk deploy cloud_run currency_agent \
  --project $PROJECT_ID \
  --region $REGION \
  --service_name currency-agent \
  --a2a \
  --env MCP_SERVER_URL="$MCP_SERVER_URL" \
  --env GOOGLE_GENAI_USE_ENTERPRISE="true" \
  --env GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
  --env GOOGLE_CLOUD_LOCATION="global" \
  -- \
  --allow-unauthenticated \
  --service-account=${SA_EMAIL}

# Capture the confirmed Cloud Run URL
CURRENCY_AGENT_URL=$(gcloud run services describe currency-agent --region $REGION --format='value(status.url)')
echo "Currency Agent URL: $CURRENCY_AGENT_URL"
```

*(Alternative with `gcloud run deploy`):*
```bash
gcloud run deploy currency-agent \
  --source currency_agent \
  --region $REGION \
  --service-account $SA_EMAIL \
  --allow-unauthenticated \
  --update-env-vars MCP_SERVER_URL="$MCP_SERVER_URL",GOOGLE_GENAI_USE_ENTERPRISE="true",GOOGLE_CLOUD_PROJECT="$PROJECT_ID",GOOGLE_CLOUD_LOCATION="global"
```

---

### Step 4: Deploy Travel Agent (ADK Web UI)

Deploy `travel_agent` with ADK Web UI enabled, `--service_name`, and the dedicated service account:

```bash
uv run adk deploy cloud_run travel_agent \
  --project $PROJECT_ID \
  --region $REGION \
  --service_name travel-agent \
  --with_ui \
  --env CURRENCY_AGENT_URL="$CURRENCY_AGENT_URL" \
  --env GOOGLE_GENAI_USE_ENTERPRISE="true" \
  --env GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
  --env GOOGLE_CLOUD_LOCATION="global" \
  -- \
  --allow-unauthenticated \
  --service-account=${SA_EMAIL}

# Capture deployed Travel Agent URL
TRAVEL_AGENT_URL=$(gcloud run services describe travel-agent --region $REGION --format='value(status.url)')
echo "Travel Agent Web UI URL: $TRAVEL_AGENT_URL"
```

---

### Step 5: Verify in Production

1. **A2A Direct Test**:
   ```bash
   AGENT_URL="$CURRENCY_AGENT_URL" uv run python currency_agent/test_a2aclient.py
   ```

2. **Web UI Test**:
   Open `$TRAVEL_AGENT_URL` in your browser and test the full multi-agent flow live on Cloud Run!

---

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
