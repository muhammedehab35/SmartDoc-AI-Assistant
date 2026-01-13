# 🏥 SmartDoc AI Assistant

<div align="center">

**AI-Powered Medical Assistant for Elderly Care**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Claude AI](https://img.shields.io/badge/Claude-Haiku-orange.svg)](https://www.anthropic.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Demo](#-quick-demo) • [Installation](#-installation) • [Architecture](#-architecture) • [Documentation](#-documentation)

---

</div>

## 🎯 Overview

**SmartDoc AI Assistant** is an intelligent medical companion designed to help elderly people manage their health through natural conversations. Powered by **Claude AI** and **LangGraph**, it provides personalized assistance for medication management, symptom analysis, and emergency detection.

### Why SmartDoc?

- 🤖 **Intelligent Classification** - Automatically understands user intent (medication, symptoms, emergency, general)
- 💊 **Medication Management** - Answers questions about medications and schedules
- 🏥 **Symptom Analysis** - Provides guidance based on reported symptoms
- 🚨 **Emergency Detection** - Recognizes urgent situations and provides immediate guidance
- 💬 **Natural Conversations** - Friendly and empathetic responses in French
- 🌐 **Modern Interface** - Clean, responsive chat UI
- 🔐 **Privacy First** - Local deployment with secure API key management

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 AI-Powered Intelligence
- Claude AI (Anthropic) for natural language understanding
- LangGraph for multi-agent orchestration
- Intent classification with 4 categories
- Context-aware responses

</td>
<td width="50%">

### 💊 Health Management
- Medication questions & reminders
- Symptom analysis & recommendations
- Emergency detection & guidance
- Medical appointment tracking

</td>
</tr>
<tr>
<td width="50%">

### 🌐 User Experience
- Modern web interface
- Real-time chat
- Easy configuration
- Mobile-responsive design

</td>
<td width="50%">

### 🏗️ Technical Excellence
- Serverless architecture ready
- AWS Lambda compatible
- Complete test suite
- Comprehensive documentation

</td>
</tr>
</table>

---

## 🚀 Quick Demo

### Example Conversations

```
👤 User: "Hello, how are you?"
🤖 Bot: "Hello Muhammad! I'm glad to meet you. How can I help you today?"

👤 User: "I have a headache"
🤖 Bot: "I understand you have a headache. Please consult your doctor.
       Meanwhile, rest and drink water..."

👤 User: "What medications should I take?"
🤖 Bot: "I cannot advise specifically on medications. Please contact
       your doctor for personalized medical advice..."

👤 User: "Medical emergency!"
🤖 Bot: "This is an emergency! Call 15 (SAMU) immediately.
       Don't stay alone..."
```

---

## 📦 Installation

### Prerequisites

- **Python 3.9+**
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/muhammedehab35/SmartDoc-AI-Assistant.git
cd SmartDoc-AI-Assistant

# 2. Create virtual environment
python -m venv env

# 3. Activate virtual environment
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
```

### Running the Application

**Windows:**
```bash
start.bat
```

**Manual Start:**
```bash
# Clear system environment variable (if any)
set ANTHROPIC_API_KEY=

# Start the server
python demo_server.py 3000
```

Then:
1. Open `frontend/index.html` in your browser
2. Click on ⚙️ settings icon
3. Configure:
   - **API URL:** `http://localhost:3000`
   - **User ID:** `user_your_name`
4. Start chatting!

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────┐
│          User Interface                  │
│      (HTML/CSS/JavaScript)               │
└──────────────┬──────────────────────────┘
               │
               ↓ HTTP POST /chat
               │
┌──────────────┴──────────────────────────┐
│       API Server (Python)                │
│       • demo_server.py                   │
│       • HTTP Server                      │
└──────────────┬──────────────────────────┘
               │
               ↓ Invoke LLM
               │
┌──────────────┴──────────────────────────┐
│       Claude AI (Anthropic)              │
│       • Intent Classification            │
│       • Response Generation              │
└──────────────┬──────────────────────────┘
               │
               ↓
┌──────────────┴──────────────────────────┐
│       User (Response Displayed)          │
└──────────────────────────────────────────┘
```

### Intent Classification

The system automatically classifies user messages into 4 categories:

| Intent | Examples | Response Strategy |
|--------|----------|-------------------|
| **general** | "Hello", "Thank you", "How are you?" | Warm, friendly conversation |
| **medication** | "What medications?", "When to take pills?" | Medical advice + consult doctor |
| **symptom** | "I have a headache", "Feeling tired" | Analysis + consultation recommendation |
| **emergency** | "Help!", "Urgent medical situation" | Immediate guidance + call emergency services |

### Multi-Agent Architecture (Ready for AWS)

```
                    Orchestrator Agent
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    Medication          Symptom           Emergency
       Agent             Agent              Agent
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                    Claude AI + DynamoDB
```

---

## 🛠️ Tech Stack

<table>
<tr>
<td><strong>Backend</strong></td>
<td>Python 3.9+, Claude AI (Anthropic), LangChain, LangGraph</td>
</tr>
<tr>
<td><strong>Frontend</strong></td>
<td>HTML5, CSS3, Vanilla JavaScript, Fetch API</td>
</tr>
<tr>
<td><strong>AI/ML</strong></td>
<td>Claude 3 Haiku, Natural Language Understanding, Intent Classification</td>
</tr>
<tr>
<td><strong>Cloud (Ready)</strong></td>
<td>AWS Lambda, DynamoDB, API Gateway, SNS, EventBridge</td>
</tr>
<tr>
<td><strong>Tools</strong></td>
<td>Git, Virtual Environments, dotenv</td>
</tr>
</table>

---

## 📁 Project Structure

```
SmartDoc-AI-Assistant/
│
├── 🚀 Core Application
│   ├── demo_server.py              # Local API server (production-ready)
│   ├── start.bat                   # Windows startup script
│   ├── requirements.txt            # Python dependencies
│   └── .env.example               # Environment template
│
├── 🌐 Frontend
│   ├── frontend/
│   │   ├── index.html             # Main interface
│   │   ├── app.js                 # Client logic
│   │   └── styles.css             # Modern design
│
├── 🤖 AI Agents (AWS Lambda Ready)
│   ├── lambda/
│   │   ├── orchestrator/          # Main router agent
│   │   ├── medication-agent/      # Medication specialist
│   │   ├── symptom-agent/         # Symptom analyzer
│   │   └── emergency-agent/       # Emergency handler
│
├── 🔧 Shared Utilities
│   ├── shared/
│   │   ├── database.py            # DynamoDB helpers
│   │   ├── utils.py               # Common utilities
│   │   └── models.py              # Data models (Pydantic)
│
├── 🧪 Testing
│   ├── test_api_key.py            # API key validation
│   ├── test_model_quick.py        # Quick Claude test
│   ├── test_langgraph.py          # Full system test
│   └── test_with_claude.py        # Orchestrator test
│
├── ☁️ Infrastructure (AWS)
│   ├── infrastructure/
│   │   └── cloudformation.yaml    # Complete AWS stack
│   └── scripts/
│       ├── deploy.sh              # Unix deployment
│       ├── deploy.bat             # Windows deployment
│       └── setup-test-data.py     # Test data creator
│
└── 📖 Documentation
    ├── README.md                  # This file
    ├── GUIDE_DEMARRAGE.md         # Complete guide (FR)
    ├── ARCHITECTURE.md            # Architecture details
    ├── RESUME_PROJET.md           # Project summary
    └── LICENSE                    # MIT License
```

---

## 🧪 Testing

### Quick Tests

```bash
# Test API key
python test_api_key.py

# Quick model test (intent classification)
python test_model_quick.py

# Full LangGraph test (orchestrator + agents)
python test_langgraph.py

# Test server health
curl http://localhost:3000/health
```

### Expected Output

```bash
$ python test_model_quick.py

Test 1: Classification
Message: "Hello" → Intent: general ✓
Message: "I have a headache" → Intent: symptom ✓
Message: "What medications?" → Intent: medication ✓

Test 2: Response Generation
Response: Natural, empathetic, contextual ✓

✅ All tests passed!
```

---

## 🌟 Usage Examples

### Via Web Interface

1. Open `frontend/index.html` in browser
2. Configure API URL and User ID
3. Start chatting!

### Via API (cURL)

```bash
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a headache",
    "userId": "user_test"
  }'
```

**Response:**
```json
{
  "response": "I understand you have a headache. Please consult your doctor...",
  "intent": "symptom",
  "userId": "user_test",
  "success": true
}
```

---

## 🔐 Security & Privacy

### Security Features

- ✅ **API Key Protection** - `.env` file never committed to Git
- ✅ **Input Validation** - All user inputs validated
- ✅ **CORS Configured** - Secure cross-origin requests
- ✅ **No Diagnosis** - Never provides medical diagnosis
- ✅ **Local First** - Can run completely offline (except API calls)

### Best Practices

```bash
# ❌ NEVER commit sensitive data
.env              # Contains API keys
*secret*          # Any secret files
*credentials*     # Credential files

# ✅ ALWAYS use .env.example as template
.env.example      # Safe template without real keys
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main documentation (this file) |
| [GUIDE_DEMARRAGE.md](GUIDE_DEMARRAGE.md) | Complete setup guide (French) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture |
| [RESUME_PROJET.md](RESUME_PROJET.md) | Project summary |
| [DEMARRAGE_RAPIDE.txt](DEMARRAGE_RAPIDE.txt) | Quick start guide |

---

## 🗺️ Roadmap

### ✅ Phase 1: MVP Local (Completed)
- ✅ Local API server
- ✅ Intent classification
- ✅ Web interface
- ✅ Complete testing

### 🚧 Phase 2: Multi-Agent (In Progress)
- 🚧 Full LangGraph orchestration
- 🚧 Specialized independent agents
- 🚧 Local database (SQLite)
- 🚧 Conversation history

### 🔮 Phase 3: AWS Production (Planned)
- 🔮 AWS Lambda deployment
- 🔮 DynamoDB persistence
- 🔮 SNS SMS notifications
- 🔮 EventBridge automated reminders
- 🔮 CloudWatch monitoring

### 🎯 Phase 4: Advanced Features (Vision)
- 🎯 Voice recognition & synthesis
- 🎯 Mobile application
- 🎯 Multi-language support
- 🎯 Doctor integrations
- 🎯 Family dashboard

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Add docstrings to functions
- Write tests for new features
- Update documentation

---

## 💡 Troubleshooting

<details>
<summary><strong>❌ Error 401: Invalid API Key</strong></summary>

**Solution:**
1. Check that `.env` contains your real Anthropic API key
2. Make sure to unset system environment variable:
   ```bash
   # Windows
   set ANTHROPIC_API_KEY=

   # Linux/Mac
   unset ANTHROPIC_API_KEY
   ```
3. Restart the server
</details>

<details>
<summary><strong>❌ Port 3000 Already in Use</strong></summary>

**Solution:**
```bash
# Use a different port
python demo_server.py 8080
```

Or kill the process using port 3000:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill
```
</details>

<details>
<summary><strong>❌ ModuleNotFoundError</strong></summary>

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```
</details>

---

## 📊 Project Statistics

```
📦 Lines of Code:      8,555+
📁 Files:              47
🤖 AI Agents:          4
🧪 Tests:              6
📖 Documentation:      7 files
⭐ Technologies:       10+
🌐 Languages:          Python, JavaScript, HTML/CSS
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Key Points:**
- ✅ Free to use, modify, and distribute
- ✅ Commercial use allowed
- ✅ Attribution required
- ✅ No warranty provided

---

## 👤 Author

**Muhammad Ehab**

- 🔗 GitHub: [@muhammedehab35](https://github.com/muhammedehab35)
- 📧 Email: [Contact](mailto:muhammedehab35@github.com)
- 💼 LinkedIn: [Connect](https://linkedin.com/in/muhammad-ehab)

---

## 🙏 Acknowledgments

Special thanks to:

- **[Anthropic](https://www.anthropic.com/)** - For Claude AI
- **[LangChain](https://www.langchain.com/)** - For the AI framework
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - For multi-agent orchestration
- **Open Source Community** - For amazing tools and libraries

---

## ⚠️ Disclaimer

**IMPORTANT:** This is a demonstration project and should **NOT** be used as a substitute for professional medical advice, diagnosis, or treatment.

Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

**Never disregard professional medical advice or delay in seeking it because of something you have read or received from this application.**

---

## 📞 Support & Contact

### Need Help?

- 📖 **Documentation**: Check the [docs folder](./docs)
- 🐛 **Bug Reports**: [Open an issue](https://github.com/muhammedehab35/SmartDoc-AI-Assistant/issues)
- 💬 **Questions**: [Start a discussion](https://github.com/muhammedehab35/SmartDoc-AI-Assistant/discussions)
- ⭐ **Feature Requests**: [Request a feature](https://github.com/muhammedehab35/SmartDoc-AI-Assistant/issues/new)

---

## 🌟 Show Your Support

If you find this project helpful, please consider:

- ⭐ **Starring** this repository
- 🔄 **Sharing** with others
- 🐛 **Reporting** bugs
- 💡 **Suggesting** features
- 🤝 **Contributing** code

---

<div align="center">

**Made with ❤️ for helping seniors stay healthy and independent**

[⬆ Back to Top](#-smartdoc-ai-assistant)

</div>
