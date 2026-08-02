# 🔎 GitHub Repository Explainer

An AI-powered **GitHub Repository Explainer** that analyzes public GitHub repositories using **LangGraph**, **LangChain**, **NVIDIA AI**, **LangSmith**, and **Retrieval-Augmented Generation (RAG)**.

The application helps developers quickly understand unfamiliar repositories by automatically generating documentation, architecture summaries, dependency analysis, code quality insights, and an interactive repository-aware chat interface.

---

## 🚀 Features

### Repository Analysis

* Clone any public GitHub repository
* Retrieve repository metadata using the GitHub API
* Scan repository structure
* Build an organized file tree

### AI Documentation

* README summarization
* Repository purpose
* Key features
* Installation instructions
* Usage overview

### Technology Stack Detection

Automatically identifies:

* Programming languages
* Frameworks
* Libraries
* Build tools
* Package managers
* Databases
* Configuration files

### Architecture Analysis

Generates:

* High-level architecture overview
* Component relationships
* Module responsibilities
* Application workflow
* Design insights

### Dependency Analysis

Extracts and explains dependencies from:

* `requirements.txt`
* `pyproject.toml`
* `package.json`
* `pom.xml`
* `build.gradle`
* Other supported dependency files

### API Discovery

Automatically detects:

* REST APIs
* FastAPI routes
* Flask routes
* Django endpoints
* Express.js APIs
* GraphQL endpoints

### Code Quality Analysis

Detects:

* TODO comments
* Large source files
* Potential dead code
* Duplicate code patterns
* Static analysis findings


# 🏗 Architecture

<img width="1536" height="1024" alt="git_exp_agi" src="https://github.com/user-attachments/assets/586fb263-f497-4a0a-9ff1-8a3519148160" />


# 🤖 Multi-Agent Workflow

The project uses multiple AI agents coordinated with **LangGraph**.

| Agent               | Responsibility                                                               |
| ------------------- | ---------------------------------------------------------------------------- |
| Documentation Agent | Summarizes README, project purpose, setup instructions, and technology stack |
| Architecture Agent  | Explains architecture, code flow, modules, and APIs                          |
| Report Builder      | Combines analysis into a final report                                        |
| Repository Chat     | Answers repository-specific questions using RAG                              |

---

# 📂 Project Structure

```text
github-repo-explainer/
│
├── app.py
├── pyproject.toml
├── .env
│
└── src/
    ├── agents/
    ├── github_client/
    ├── graph/
    ├── models/
    ├── parsers/
    ├── rag/
    ├── scanners/
    ├── services/
    └── config.py
```

---

# ⚙️ Technology Stack

* Python
* Streamlit
* LangChain
* LangGraph
* NVIDIA AI Inference API
* LangSmith
* GitPython
* PyGithub
* FAISS (or another vector database)
* Pydantic

---

# 🔄 Analysis Pipeline

```text
GitHub URL
      │
      ▼
Fetch Repository Metadata
      │
      ▼
Clone Repository
      │
      ▼
Scan Important Files
      │
      ▼
Parallel Static Analysis
      │
      ├── Dependency Detection
      ├── API Discovery
      ├── Entry Point Detection
      └── Code Quality Checks
      │
      ▼
Documentation Agent
      │
      ▼
Architecture Agent
      │
      ▼
Final Repository Report
      │
      ▼
Repository Chat (RAG)
```

---

# 💬 Example Questions

* What does this repository do?
* Explain the project architecture.
* What technologies are used?
* Which file is the application entry point?
* How does data flow through the project?
* Where is authentication implemented?
* Explain the dependency structure.
* Which APIs are exposed?
* Summarize the README.
* Which files should I read first?
* Where are the database models located?
* Explain the OCR pipeline.
* Show the technology stack.
* Which modules are responsible for business logic?

---

# 📊 Outputs

The application generates:

* Repository overview
* README summary
* Technology stack
* Architecture explanation
* Dependency report
* API documentation
* Code quality report
* Repository statistics
* Interactive repository chat

---
