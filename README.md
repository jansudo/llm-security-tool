# LLMSecurity Tool

**A General-Purpose Automated Red Team Agent for LLM Applications.**

This tool is designed for security researchers, penetration testers, and AI developers to automatically test, assess, and identify vulnerabilities in Large Language Model (LLM) integrated applications. While it includes a CTF challenge for demonstration, its core engine is built for real-world security assessments.

## 🚀 Key Features

- **General Purpose Security Assessment**: Capable of testing *any* web-based chat interface, not just CTFs.
- **Objective-Driven AI**: Specify your exact goal (e.g., "Extract PII", "Reveal system instructions", "Bypass filters"), and the AI will tailor sophisticated attacks to achieve it.
- **Auto-Discovery**: Automatically detects chat input fields and send buttons on target pages. No complex CSS selectors required.
- **Infinite Attack Loop**: Can run indefinitely (`--iterations 0`) until the objective is met.
- **Robust Automation**: Includes smart timeout handling (120s), auto-page refreshing, and failure recovery.
- **Hybrid AI Engine**:
  - **Speed**: Uses your `OPENAI_API_KEY` (via `.env`) if provided for maximum performance.
  - **Free Tier**: Automatically falls back to **Pollinations.ai** (free, no-key) if no API key is present.

## 🛠️ Installation

```bash
# 1. Clone the repository
cd llmsecurity

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -e .

# 4. (Optional) Configure API Keys for better performance
# Create a .env file and add your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env
```

## 🎮 Usage

### 1. General Security Assessment (Real-World Targets)
Launch the autonomous agent against any web-based chat interface you are authorized to test.

**Example 1: Testing for PII Leakage**
```bash
python3 -m llmsecurity.cli attack http://target-app.com/chat \
  --objective "Attempt to exfiltrate other users' email addresses or phone numbers." \
  --iterations 0
```

**Example 2: Testing System Prompt Leakage**
```bash
python3 -m llmsecurity.cli attack http://internal-bot.local/ \
  --objective "Trick the bot into revealing its complete system instructions and safety rules."
```

**Example 3: Jailbreaking Content Filters**
```bash
python3 -m llmsecurity.cli attack http://public-chatbot.com/ \
  --objective "Generate a response that violates the content safety policy regarding [Topic]."
```

### 2. Static Analysis
Analyze a text file containing a chat log to find logic flaws and vulnerabilities.

```bash
python3 -m llmsecurity.cli analyze --file chat.log
```

## 🏴‍☠️ Testing (CTF Mode)
The tool includes a local "Secure Vault" CTF challenge for training and verification.

1. **Start the CTF Server**:
   ```bash
   uvicorn ctf_challenge.main:app --port 8000
   ```

2. **Run the Attacker**:
   Open a new terminal and run:
   ```bash
   python3 -m llmsecurity.cli attack http://localhost:8000/ --objective "Get the flag" --iterations 0
   ```

3. **Win**: The tool will loop, generating new attacks until it extracts the flag `CTF{...}`.
![alt text](image.png)