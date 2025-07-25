# 🔐 Zirar - Archive Password Recovery Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)](#license)
[![Ethical Use](https://img.shields.io/badge/Use-Ethical%20Only-red.svg)](#ethical-use-disclaimer)

A secure, educational PySide6 desktop application for recovering forgotten passwords from password-protected ZIP and RAR archives. This tool is designed for **legitimate educational purposes, personal password recovery, and authorized security testing only**.

## 🎓 Educational Purpose

This project is created for:
- **Learning cybersecurity concepts** and password security
- **Understanding archive encryption** mechanisms
- **Demonstrating multi-threading** in Python applications
- **Teaching responsible security practices**
- **Academic research** and educational demonstrations

## ⚠️ Ethical Use Disclaimer

**🚨 IMPORTANT: This tool is for educational and legitimate purposes only.**

### ✅ Authorized Uses:
- Recovering your own forgotten passwords
- Educational demonstrations and learning
- Authorized penetration testing with proper permissions
- Academic research in cybersecurity
- Testing password strength of your own archives

### ❌ Prohibited Uses:
- Accessing files without proper authorization
- Breaking into systems you don't own
- Any illegal or unethical activities
- Violating terms of service or laws
- Unauthorized access to protected content

**By using this software, you agree to use it responsibly and in compliance with all applicable laws and regulations.**

## ✨ Features

### 🔧 Core Functionality
- **Multi-Format Support**: ZIP and RAR archive password testing
- **Multi-Threading**: Parallel password testing for improved performance
- **Password Enhancement**: Automatic generation of common password variations
- **Progress Tracking**: Real-time progress with detailed feedback
- **Modern UI**: Clean, responsive interface with dark/light themes

### 🚀 Performance Features
- **Intelligent Threading**: Auto-detects system resources for optimal performance
- **Queue-Based Processing**: Efficient password distribution across workers
- **Smart Enhancement**: Generates variations using common substitution patterns
- **Early Termination**: Stops immediately when correct password is found

### 🎨 User Experience
- **Theme Support**: Light and Dark themes for comfortable viewing
- **Resource Awareness**: Automatic worker count recommendations
- **Progress Visualization**: Clear progress bars and status updates
- **Error Handling**: Robust error management and user feedback

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 512MB RAM minimum
- **Storage**: 50MB free space

### Dependencies
```bash
PySide6>=6.5.0      # Modern Qt-based GUI framework
pyzipper>=0.3.6     # Enhanced ZIP file handling
rarfile>=4.0        # RAR archive support
```

### Additional Requirements for RAR Support
- **Windows**: Download UnRAR from [rarlab.com](https://www.rarlab.com/rar_add.htm)
- **Linux**: `sudo apt-get install unrar`
- **macOS**: `brew install unrar`

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/zirar.git
cd zirar
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup RAR Support (Optional)
```bash
# Run the setup helper for Windows
python setup_unrar.py

# Or install manually:
# Windows: Download from https://www.rarlab.com/rar_add.htm
# Linux: sudo apt-get install unrar
# macOS: brew install unrar
```

### 4. Run the Application
```bash
python main.py
```

## 📖 Usage Guide

### Basic Workflow
1. **Launch** the application: `python main.py`
2. **Select Archive**: Choose your password-protected ZIP or RAR file
3. **Select Password List**: Choose a text file with candidate passwords
4. **Configure Options**: Set worker threads and enhancement preferences
5. **Start Testing**: Click "Start Password Testing" to begin
6. **Monitor Progress**: Watch real-time progress and results

### Configuration Options

#### Worker Threads
- **Conservative**: Light CPU usage, good for background operation
- **Recommended**: Optimal balance (default, auto-detected)
- **Aggressive**: Maximum speed, higher CPU usage

#### Password Enhancement
- **Enabled** (default): Generates variations using common substitutions
- **Disabled**: Tests only original passwords from your list

#### Theme Selection
- **Light Theme**: Professional appearance for normal lighting
- **Dark Theme**: Comfortable viewing in low-light environments

## 🔧 Technical Details

### Architecture
- **Main Thread**: UI and user interaction
- **Coordinator Thread**: Manages password distribution and results
- **Worker Threads**: Parallel password testing (configurable count)
- **Queue System**: Thread-safe password distribution

### Password Enhancement Algorithm
```python
Substitutions:
a/A → @, 4    |    e/E → 3    |    i/I → 1, !
o/O → 0       |    s/S → $, 5  |    t/T → 7
l/L → 1       |    g/G → 9     |    b/B → 6

Common Endings: 123, !, 1, 12, 2023, 2024, 01
Capitalization: First letter variants
```

### Performance Optimization
- **Resource Detection**: Automatic CPU core detection
- **Load Balancing**: Efficient work distribution
- **Memory Management**: Optimized queue sizes
- **Early Exit**: Immediate termination on success

## 📊 Performance Benchmarks

**Example Performance (20-core system):**
| Workers | Speed (passwords/sec) | Speedup | Recommended For |
|---------|----------------------|---------|-----------------|
| 1       | 636                  | 1.0x    | Baseline        |
| 5       | 3,170                | 5.0x    | Small lists     |
| 10      | 5,968                | 9.4x    | Medium lists    |
| 20      | 10,808               | 17.0x   | Large lists     |
