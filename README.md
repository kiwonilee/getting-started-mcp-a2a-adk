# ADK를 활용한 MCP & A2A 시작하기

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg)](https://github.com/google/adk-python)
[![Protocol](https://img.shields.io/badge/Protocol-A2A-34A853.svg)](https://github.com/google-a2a/a2a-python)
[![Protocol](https://img.shields.io/badge/Protocol-MCP-EA4335.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**[한국어](#adk를-활용한-mcp--a2a-시작하기)** | **[English](#getting-started-with-mcp--a2a-with-adk)**

**Model Context Protocol (MCP)**과 **Agent2Agent (A2A)**가 **Agent Development Kit (ADK)**와 함께 상호작용하는 샘플 멀티 에이전트 시스템입니다.
모든 서비스는 ADK 모범 사례(Best Practices)를 준수하며, ADK CLI를 통해 로컬에서 완전히 실행하거나 Google Cloud Run에 배포할 수 있습니다.

![Architecture Overview](images/architecture.png)

---

## 개요 (Overview)

이 샘플은 MCP + A2A + ADK 기술 스택의 모범 사례를 제시하며, 깔끔하고 프로덕션 환경에 바로 적용할 수 있는 기반 아키텍처를 제공합니다.

### <img height="20" width="20" src="images/mcp-favicon.ico" alt="MCP Logo" /> Model Context Protocol (MCP)

> MCP는 애플리케이션이 LLM에 컨텍스트를 제공하는 방식을 표준화하는 오픈 프로토콜입니다. MCP를 AI 애플리케이션을 위한 USB-C 포트라고 생각하면 쉽습니다. USB-C가 디바이스를 다양한 주변기기에 연결하는 표준화된 방식을 제공하듯, MCP는 AI 모델을 다양한 데이터 소스 및 도구와 연결하는 표준 방식을 제공합니다. - [Anthropic](https://modelcontextprotocol.io/introduction)

이 예제의 MCP 서버는 USD, EUR 등 두 통화 간의 환율을 조회할 수 있는 `get_exchange_rate` 도구를 제공합니다. 공개 [Frankfurter](https://www.frankfurter.dev/) API를 활용하여 실시간 환율을 가져오며, 에이전트는 MCP 클라이언트를 사용하여 필요할 때 이 도구를 호출합니다.

### <img height="20" width="20" src="https://a2a-protocol.org/v0.2.5/assets/a2a-logo-black.svg" alt="A2A Logo" /> Agent2Agent (A2A)

> Agent2Agent (A2A) 프로토콜은 AI 생태계의 핵심 과제를 해결합니다. 서로 다른 기업이 다양한 프레임워크로 구축하고 별도의 서버에서 실행하는 생성형 AI 에이전트들이 단순한 도구가 아니라 '에이전트 대 에이전트'로서 효과적으로 소통하고 협업할 수 있도록 지원합니다. A2A는 에이전트 간 공통 언어를 제공하여 상호 연결되고 강력한 AI 생태계를 조성합니다. - [A2A](https://github.com/a2aproject/A2A)

본 샘플에서 에이전트는 **관심사 분리(Separation of Concerns, SoC)** 모범 사례를 따릅니다:
- **순수 에이전트 정의 (Pure Agent Definition)**: `currency_agent/agent.py`는 복잡한 서버나 프로토콜 보일러플레이트 코드 없이 에이전트 정의(`root_agent = LlmAgent(...)`)만 포함합니다.
- **A2A Agent Card 사전 생성 (A2A Agent Card Pre-generation)**: Agent Card(`currency_agent/agent.json`)는 `generate_card.py`를 통해 사전에 한 번 생성됩니다.
- **A2A 인터페이스 노출 (A2A Exposure)**: ADK 내장 서버(`adk api_server --a2a` 또는 `adk deploy cloud_run --a2a`)를 통해 손쉽게 A2A 엔드포인트로 노출됩니다.
- **원격 에이전트 호출 (Remote Consumption)**: `travel_agent`는 `RemoteA2aAgent`를 사용하여 `currency_agent`를 원격 도구로 호출합니다.

### <img height="20" width="20" src="images/adk-favicon.ico" alt="ADK Logo" /> Agent Development Kit (ADK)

> ADK는 AI 에이전트를 개발하고 배포하기 위한 유연하고 모듈화된 프레임워크입니다. Gemini 및 Google 생태계에 최적화되어 있으면서도 모델 및 배포 환경에 구애받지 않으며, 다른 프레임워크와의 뛰어난 호환성을 갖추고 있습니다. - [ADK](https://github.com/google/adk-python)

ADK는 핵심 오케스트레이션 프레임워크로 사용됩니다. 에이전트 정의 관리, 도구 호출(MCP 포함) 실행, Web UI 제공, JSON-RPC A2A 라우팅 처리, 로컬 개발 및 클라우드 배포를 위한 CLI 도구를 제공합니다.

---

## 🏗️ 아키텍처 개요 (Architecture Overview)

시스템은 Web UI를 제공하는 1개의 오케스트레이터 에이전트, A2A를 통한 1개의 원격 에이전트, 1개의 로컬 에이전트 도구, 그리고 1개의 MCP 서버로 구성됩니다:

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

### 핵심 구성 요소

- **`currency_mcp_server/`**: Streamable HTTP(`/mcp`)를 통해 `get_exchange_rate` 도구를 제공하는 FastMCP 서버이며, 공개 [Frankfurter API](https://api.frankfurter.dev/)를 사용합니다.
- **`currency_agent/`**: 
  - `agent.py`: 순수 ADK `LlmAgent` 정의입니다. 단독 실행하거나 A2A로 노출할 수 있습니다.
  - `generate_card.py`: A2A 규격의 `agent.json`을 사전에 생성하는 스크립트입니다.
  - `agent.json`: ADK가 A2A 라우트를 마운트하는 데 사용하는 표준 A2A Agent Card입니다.
- **`travel_agent/`**: 다음 두 에이전트를 오케스트레이션하는 여행 보조 ADK 에이전트입니다:
  - **`weather_agent`**: 프로세스 내(in-process)에서 직접 실행되는 **로컬 에이전트 도구(`AgentTool`)**로 네트워크 지연 없이 즉시 동작합니다.
  - **`currency_agent`**: A2A 프로토콜을 통해 요청을 위임하는 **원격 에이전트 도구(`AgentTool`)**입니다.

---

## 📦 의존성 관리 (`uv` Workspace)

프로젝트 의존성은 통합 **`uv` Workspace**로 관리됩니다:
- 루트 `pyproject.toml`이 워크스페이스 멤버(`currency_mcp_server`, `currency_agent`, `travel_agent`)를 통합 관리합니다.
- 루트에서 `uv sync`를 실행하면 로컬 개발에 필요한 모든 패키지가 단일 `.venv`에 자동으로 해결 및 설치됩니다.
- 각 서비스 디렉토리는 독립적인 빌드와 배포를 위해 자체 `pyproject.toml`을 보유합니다.

---

## 🚀 시작하기 (Getting Started)

### 사전 요구사항

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation):
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Cloud Run 배포 시: Google Cloud SDK (`gcloud`)

### 설치 방법

1. 리포지토리 클론:
   ```bash
   git clone https://github.com/kiwonlee/getting-started-mcp-a2a-adk.git
   cd getting-started-mcp-a2a-adk
   ```

2. 워크스페이스 전체 의존성 설치:
   ```bash
   uv sync
   ```

3. 환경 변수 설정:
   프로젝트 루트에 `.env` 파일을 생성합니다:
   
   ```sh
   cp .env.example .env
   ```
   
   ```sh
   GOOGLE_GENAI_USE_ENTERPRISE=TRUE
   GOOGLE_CLOUD_PROJECT=<your_gcp_project_id>
   GOOGLE_CLOUD_LOCATION=global
   ```

---

## ☁️ Cloud Run 배포 (Cloud Run Deployment)

모든 구성 요소는 Google Cloud Run에 깔끔하게 배포할 수 있습니다. ADK 내장 명령어인 `adk deploy cloud_run` 또는 표준 `gcloud run deploy` 명령어를 사용할 수 있습니다.

### 환경 설정

Google Cloud 프로젝트, 리전 및 전용 서비스 계정 정보를 설정합니다:

```bash
export PROJECT_ID=<YOUR_GOOGLE_CLOUD_PROJECT_ID>
export REGION=us-central1
export SA_NAME="getting-started-mcp-a2a-adk"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```

필요한 GCP API 활성화:

```bash
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       aiplatform.googleapis.com
```

MCP 서버 및 ADK 에이전트 실행에 사용할 전용 서비스 계정을 생성하고 필수 권한을 부여합니다:

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# 1. 전용 서비스 계정 생성
gcloud iam service-accounts create $SA_NAME \
    --display-name="Getting-started-mcp-a2a-adk Service Account"

# 2. 런타임(Vertex AI, 로깅) 및 빌드 권한 부여
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

### Step 1: Currency MCP Server 배포

전용 서비스 계정을 사용하여 FastMCP 서버를 배포합니다:

```bash
gcloud run deploy currency-mcp-server \
  --source currency_mcp_server \
  --region $REGION \
  --service-account $SA_EMAIL \
  --allow-unauthenticated

# 배포된 MCP 서버 URL 캡처
MCP_SERVER_URL=$(gcloud run services describe currency-mcp-server --region $REGION --format='value(status.url)')/mcp
echo "MCP Server URL: $MCP_SERVER_URL"
```

---

### Step 2: 대상 URL 확인 및 Currency Agent Card (`agent.json`) 생성

`currency_agent`를 배포하기 전에 A2A Agent Card(`agent.json`)를 먼저 생성합니다.

> [!IMPORTANT]
> **배포 전에 `agent.json`을 생성해야 하는 이유**:
> 1. **A2A 라우트 패키징**: ADK의 `adk deploy cloud_run --a2a`는 빌드 시점에 `agent.json`을 Docker 이미지에 포함합니다. 빌드 시 `agent.json`이 누락되면 A2A 엔드포인트(`/a2a/currency_agent`)가 마운트되지 않습니다.
> 2. **접근 가능한 RPC 대상 명시**: `agent.json`의 `supportedInterfaces`는 A2A 클라이언트가 RPC 호출을 보낼 위치를 안내합니다. 따라서 `localhost`가 아닌 실제 Cloud Run 엔드포인트(`https://.../a2a/currency_agent`)가 포함되어야 합니다.
> 3. **결정론적인 Cloud Run 도메인**: 동일한 프로젝트와 리전의 Cloud Run 서비스는 동일한 도메인 접미사(domain suffix)를 공유합니다. 따라서 이미 배포된 `currency-mcp-server`의 URL을 통해 `currency-agent`의 URL을 사전에 예측하여 2번 배포할 필요 없이 한 번에 구성할 수 있습니다.

대상 URL을 확인하고 카드를 생성합니다:

```bash
# 1. Currency Agent 대상 URL 결정 (기존 서비스 조회 또는 MCP 서버 도메인 기반 예측)
CURRENCY_AGENT_URL=$(gcloud run services describe currency-agent --region $REGION --format='value(status.url)' 2>/dev/null || echo "")

if [ -z "$CURRENCY_AGENT_URL" ]; then
  DOMAIN_SUFFIX=$(gcloud run services describe currency-mcp-server --region $REGION --format='value(status.url)' | sed 's/.*currency-mcp-server//')
  CURRENCY_AGENT_URL="https://currency-agent${DOMAIN_SUFFIX}"
fi
echo "Target Currency Agent URL: $CURRENCY_AGENT_URL"

# 2. MCP 도구 및 Cloud Run RPC URL 정보를 담은 agent.json 생성
MCP_SERVER_URL="$MCP_SERVER_URL" uv run python -m currency_agent.generate_card --url "${CURRENCY_AGENT_URL}/a2a/currency_agent"
```
```bash
cat ./currency_agent/agent.json
```
---

### Step 3: Currency Agent 배포 (ADK with A2A)

ADK의 `adk deploy cloud_run` 명령어를 사용하여 배포합니다. `--service_name`, `--a2a` 옵션을 지정하고 `--` 구분자 뒤에 `gcloud` 플래그를 전달합니다:

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

# 배포된 Cloud Run URL 확인
CURRENCY_AGENT_URL=$(gcloud run services describe currency-agent --region $REGION --format='value(status.url)')
echo "Currency Agent URL: $CURRENCY_AGENT_URL"
```

*(대안: `gcloud run deploy` 직접 사용 시):*
```bash
gcloud run deploy currency-agent \
  --source currency_agent \
  --region $REGION \
  --service-account $SA_EMAIL \
  --allow-unauthenticated \
  --update-env-vars MCP_SERVER_URL="$MCP_SERVER_URL",GOOGLE_GENAI_USE_ENTERPRISE="true",GOOGLE_CLOUD_PROJECT="$PROJECT_ID",GOOGLE_CLOUD_LOCATION="global"
```

---

### Step 4: Travel Agent 배포 (ADK Web UI)

ADK Web UI를 활성화(`--with_ui`)하고 전용 서비스 계정을 연결하여 `travel_agent`를 배포합니다:

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

# 배포된 Travel Agent Web UI URL 확인
TRAVEL_AGENT_URL=$(gcloud run services describe travel-agent --region $REGION --format='value(status.url)')
echo "Travel Agent Web UI URL: $TRAVEL_AGENT_URL"
```

---

### Step 5: 프로덕션 환경 검증

1. **A2A 직접 호출 테스트**:
   ```bash
   AGENT_URL="$CURRENCY_AGENT_URL" uv run python currency_agent/test_a2aclient.py
   ```

2. **Web UI 테스트**:
   브라우저에서 `$TRAVEL_AGENT_URL` 주소로 접속하여 Cloud Run에서 구동 중인 멀티 에이전트 시스템 전체 흐름을 테스트합니다!
   > 예시 질문: *"도쿄로 여행을 가려고 해. 날씨는 어떻고 500달러는 엔화로 얼마야?"*

---

## 📄 라이선스 (License)

이 프로젝트는 Apache 2.0 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

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
