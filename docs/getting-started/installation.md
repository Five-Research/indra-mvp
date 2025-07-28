# Installation Guide

Getting Indra up and running on your system is quick and easy. This guide will walk you through everything you need to know.

## 📋 Prerequisites

Before installing Indra, make sure you have:

- **Python 3.8 or higher** - Check with `python --version`
- **OpenAI API key** - Get one from [OpenAI's website](https://platform.openai.com/api-keys)
- **Git** (optional) - For cloning the repository

## 🚀 Quick Installation

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/Five-Research/indra-mvp.git
cd indra-mvp

# Install in development mode
pip install -e .

# Verify installation
indra status
```

### Option 2: Direct Download

If you don't have Git, you can download the project directly:

1. Go to [GitHub repository](https://github.com/Five-Research/indra-mvp)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal in the extracted folder
5. Run `pip install -e .`

## 🔑 Setting Up Your API Key

Indra needs an OpenAI API key to work. Here's how to set it up:

### Method 1: Environment Variable (Recommended)

**On macOS/Linux:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**On Windows:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**To make it permanent**, add the export line to your shell profile:
```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Method 2: Pass Directly in Code

```python
from openai import OpenAI
from indra import Queen

client = OpenAI(api_key="your-api-key-here")
queen = Queen(client)
```

## ✅ Verify Installation

Let's make sure everything is working:

```bash
# Check system status
indra status

# Run the test suite
python test_framework.py

# Try a simple workflow
indra run "Plan a weekend trip to Paris"
```

If you see ✅ marks, you're all set!

## 📦 Dependencies

Indra has minimal dependencies by design:

- **openai** (≥1.0.0) - For AI model integration
- **pydantic** (≥2.0.0) - For data validation
- **python-json-logger** (≥2.0.0) - For structured logging

These are automatically installed when you run `pip install -e .`

## 🐳 Docker Installation (Optional)

If you prefer using Docker:

```bash
# Build the Docker image
docker build -t indra-mvp .

# Run Indra in a container
docker run -e OPENAI_API_KEY="your-key" indra-mvp indra status
```

## 🔧 Development Setup

If you want to contribute to Indra or modify it:

```bash
# Clone and install
git clone https://github.com/Five-Research/indra-mvp.git
cd indra-mvp
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests
python test_framework.py

# Format code
black indra/
```

## 🚨 Troubleshooting

### Common Issues

**"Command not found: indra"**
- Make sure you ran `pip install -e .` in the project directory
- Try `python -m indra.cli status` instead

**"OpenAI API key not found"**
- Double-check your API key is set correctly
- Try `echo $OPENAI_API_KEY` to verify it's set

**"Permission denied"**
- On macOS/Linux, you might need `sudo pip install -e .`
- Or use a virtual environment (recommended)

**Import errors**
- Make sure you're using Python 3.8+
- Try reinstalling: `pip uninstall indra-mvp && pip install -e .`

### Getting Help

If you're still having trouble:

1. Search [GitHub Issues](https://github.com/Five-Research/indra-mvp/issues)
2. Create a new issue with your error details

## 🎯 Next Steps

Now that Indra is installed, you're ready to:

1. **Try the Quick Start**: [Quick Start Tutorial](quick-start.md)
2. **Learn the Concepts**: [What is Indra?](../core-concepts/what-is-indra.md)
3. **Run Examples**: [Travel Planning Example](../examples/travel-planning.md)

---

*Installation complete? Great! Let's move on to the [Quick Start Tutorial](quick-start.md).*