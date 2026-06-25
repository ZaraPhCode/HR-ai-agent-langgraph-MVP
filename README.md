# 🤖 HR CV Analysis Agent with LangGraph

An intelligent, multi-provider LLM agent that automates CV screening and candidate evaluation for HR professionals. Built with LangGraph for stateful workflow orchestration.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Supported LLM Providers](#supported-llm-providers)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Technical Architecture](#technical-architecture)
- [Workflow Details](#workflow-details)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project automates the CV screening process using AI. It reads candidate information from a CSV file, analyzes each CV using a configurable LLM, and writes structured evaluation results to an output CSV.

**Key Benefits:**
- 🚀 **Automates** repetitive CV screening tasks
- 🧠 **Intelligent evaluation** with detailed scoring
- 🔄 **Idempotent processing** (no duplicate analyses)
- 💰 **Cost-effective** with multiple provider options
- 📊 **Structured output** for easy HR integration

---

## ✨ Features

- 🔄 **Multiple LLM Providers** – Seamlessly switch between OpenAI, Claude, Groq, or use mock mode for testing
- 📊 **CSV-Based Workflow** – Simple input/output with CSV files
- 🔁 **Idempotent Processing** – `is_processed` flag prevents duplicate analysis
- 🤖 **LangGraph Orchestration** – Stateful, graph-based workflow for reliable execution
- 🛡️ **Fallback & Error Handling** – Graceful degradation with mock responses
- 📈 **Structured Evaluation** – Comprehensive scoring with detailed reasoning
- 🔧 **Configurable** – Environment-based configuration for easy deployment

---

## 🔧 How It Works

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGGRAPH HR AGENT                          │
└─────────────────────────────────────────────────────────────────┘

[START]
   │
   ▼
┌─────────────────────┐
│  1. LOAD DATA       │  ← Reads input.csv, finds unprocessed rows
│  (load_data)        │     (is_processed = FALSE)
└─────────────────────┘
   │
   ▼
┌─────────────────────┐
│  2. PROCESS CV      │  ← Extracts one row at a time
│  (process_cv)       │     Job ID, Title, Description, CV
└─────────────────────┘
   │
   ▼
┌─────────────────────┐
│  3. ANALYZE WITH    │  ← Calls configured LLM provider
│     LLM             │     (OpenAI, Claude, Groq, or Mock)
│  (analyze_with_llm) │     Returns JSON with: score, summary,
│                     │     strengths, weaknesses, decision
└─────────────────────┘
   │
   ▼
┌─────────────────────┐
│  4. UPDATE RESULTS  │  ← Appends to results.csv
│  (update_results)   │     with all analysis data
└─────────────────────┘
   │
   ▼
┌─────────────────────┐
│  5. MARK PROCESSED  │  ← Sets is_processed = TRUE
│  (mark_processed)   │     in input.csv
└─────────────────────┘
   │
   ▼
  ┌─┴─┐
  │   │  More rows?
  │   │
  YES  NO
   │   │
   ▼   ▼
   back END
```

### Data Flow

1. **Input CSV** → HR adds rows with job details and CVs
2. **Agent Processing** → Each row is analyzed sequentially
3. **LLM Analysis** → Candidate is evaluated against job requirements
4. **Output CSV** → Results are written with scores and decisions
5. **Idempotency** → Processed rows are marked to prevent re-analysis

---

## 🤖 Supported LLM Providers

| Provider | Model | API Key Required | Notes |
|----------|-------|------------------|-------|
| **OpenAI** | `gpt-4o-mini` | `OPENAI_API_KEY` | Best for general use |
| **Claude** | `claude-3-5-sonnet` | `CLAUDE_API_KEY` | Strong reasoning |
| **Groq** | `openai/gpt-oss-120b` | `GROQ_API_KEY` | Fastest inference |
| **Mock** | (mock) | None | No API calls, for testing |

### Provider Selection

Set `LLM_PROVIDER` in `.env` to one of: `openai`, `claude`, `groq`, or `mock`

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hr-agent-langgraph.git
cd hr-agent-langgraph
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your chosen provider and API key
```

### 5. Verify Installation

```bash
python -c "import pandas; import langgraph; print('All dependencies installed!')"
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider to use: `openai`, `claude`, `groq`, `mock` | `groq` |
| `OPENAI_API_KEY` | OpenAI API key | (empty) |
| `CLAUDE_API_KEY` | Claude API key | (empty) |
| `GROQ_API_KEY` | Groq API key | (empty) |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |
| `CLAUDE_MODEL` | Claude model name | `claude-3-5-sonnet-20241022` |
| `GROQ_MODEL` | Groq model name | `openai/gpt-oss-120b` |
| `INPUT_FILE` | Input CSV file path | `input.csv` |
| `RESULTS_FILE` | Results CSV file path | `results.csv` |

### Sample `.env` File

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here

# Or for OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_api_key_here

# Or for Claude:
# LLM_PROVIDER=claude
# CLAUDE_API_KEY=your_claude_api_key_here

# Or for testing without API:
# LLM_PROVIDER=mock
```

---

## 🚀 Usage

### 1. Prepare Input CSV

Create `input.csv` with the following columns:

```csv
Job ID,Position Title,Position Description,Candidate Name,CV Content,is_processed
JOB001,Software Engineer,"We are looking for a Software Engineer with 5+ years in Python, Django, PostgreSQL, and AWS.",John Doe,"John Doe\nEmail: john@email.com\n\nSummary: Software Engineer with 7 years experience...\n\nSkills: Python, Django, PostgreSQL, AWS, Docker",FALSE
JOB002,Data Analyst,"Looking for a Data Analyst with SQL, Python, and Tableau experience.",Jane Smith,"Jane Smith\nEmail: jane@email.com\n\nSummary: Data Analyst with 5 years experience...\n\nSkills: SQL, Python, Tableau, Power BI",FALSE
```

### 2. Run the Agent

```bash
python main.py
```

### 3. Check Results

Open `results.csv` to see the analysis:

```csv
Job ID,Position Title,Candidate Name,Match Score,CV Summary,Strengths,Weaknesses,Call Applicant,Decision,Reasoning,Processed Date
JOB001,Software Engineer,John Doe,92,"John Doe is a software engineer with 7 years full-stack experience...","Python, Django, AWS, Docker; Full-stack expertise; 7 years experience","Limited project details; No testing/CI/CD; No leadership",TRUE,HIRE,"Strong match with required skills",2026-06-25 10:30:00
```

---

## 📁 File Structure

```
hr_agent_langgraph/
├── main.py                 # Main entry point
├── agent.py               # LangGraph agent definition
├── tools.py               # Tools for CSV operations
├── state.py               # State definition for the agent
├── llm_client.py          # Multi-provider LLM client
├── config.py              # Configuration management
├── input.csv              # Input file with CVs to process
├── results.csv            # Output file with analysis results
├── requirements.txt       # Python dependencies
├── .env                   # API keys configuration
├── .env.example           # Example configuration file
└── README.md              # This file
```

---

## 🏗️ Technical Architecture

### LangGraph Workflow

The agent uses LangGraph's `StateGraph` to define a stateful workflow:

1. **`load_data`** – Reads the input CSV and identifies unprocessed rows
2. **`process_cv`** – Extracts the current row's data
3. **`analyze_with_llm`** – Calls the LLM provider to analyze the CV
4. **`update_results`** – Appends results to the output CSV
5. **`mark_processed`** – Updates the `is_processed` flag in the input CSV

### Conditional Routing

The workflow includes a conditional edge that checks if there are more rows to process:

```python
workflow.add_conditional_edges(
    "mark_processed",
    self.should_continue,
    {
        "continue": "process_cv",  # Process next row
        "end": END                 # All done
    }
)
```

### LLM Client Abstraction

The `LLMClient` class provides a unified interface for multiple providers:

```python
# Usage example
client = LLMClient('groq')  # or 'openai', 'claude', 'mock'
result = client.analyze_cv(
    job_id='JOB001',
    position_title='Software Engineer',
    position_description='...',
    candidate_name='John Doe',
    cv_content='...'
)
```

---

## 🔬 Workflow Details

### Input CSV Schema

| Column | Description | Required |
|--------|-------------|----------|
| `Job ID` | Unique identifier for the position | ✅ |
| `Position Title` | Title of the position | ✅ |
| `Position Description` | Full job description | ✅ |
| `Candidate Name` | Full name of the candidate | ✅ |
| `CV Content` | Full CV text | ✅ |
| `is_processed` | `TRUE`/`FALSE` – processed flag | Optional |

### Output CSV Schema

| Column | Description |
|--------|-------------|
| `Job ID` | Unique identifier from input |
| `Position Title` | Title from input |
| `Candidate Name` | Name from input |
| `Match Score` | Percentage score (0-100) |
| `CV Summary` | 2-3 sentence summary |
| `Strengths` | Top 3 strengths (comma separated) |
| `Weaknesses` | Top 3 weaknesses (comma separated) |
| `Call Applicant` | `TRUE`/`FALSE` – whether to call |
| `Decision` | `HIRE`/`CONSIDER`/`REJECT` |
| `Reasoning` | Explanation of decision |
| `Processed Date` | Timestamp of processing |

### LLM Evaluation Criteria

The LLM evaluates candidates based on:

1. **Experience Match** – Years and relevance of experience
2. **Skill Alignment** – Match with required skills
3. **Cultural Fit** – Soft skills and communication
4. **Growth Potential** – Learning and adaptability
5. **Decision Reasoning** – Clear justification

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### 2. "API key not found"
```bash
# Check your .env file
cat .env
# Ensure the API key is set correctly
```

#### 3. "No unprocessed rows found"
```bash
# Check input.csv has rows with is_processed = FALSE
# Or add new rows
```

#### 4. "Recursion limit reached"
```python
# In agent.py, increase recursion_limit
final_state = self.app.invoke(initial_state, {"recursion_limit": 1000})
```

#### 5. "Provider not supported"
```bash
# Check LLM_PROVIDER in .env
# Valid values: openai, claude, groq, mock
```

### Debug Mode

Set `LLM_PROVIDER=mock` to run without API calls for testing.

---

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License – see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [LangChain](https://github.com/langchain-ai/langchain) for LLM integration
- [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), and [Groq](https://groq.com/) for LLM APIs

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for HR teams everywhere**