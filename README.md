# Zirar - Archive Password Cracker

A secure PySide6 desktop application for testing passwords against password-protected ZIP and RAR archives.

## Features

- Support for both ZIP and RAR archives
- Threaded password testing for responsive UI
- Progress tracking with detailed feedback
- Modern, clean user interface
- Security-focused design with proper error handling
- Ethical use guidelines and password strength recommendations

## Requirements

- Python 3.8+
- PySide6
- pyzipper (for ZIP files)
- rarfile (for RAR files)
- UnRAR executable (for RAR support)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For RAR support, install UnRAR:
   - Windows: Download from https://www.rarlab.com/rar_add.htm
   - Linux: `sudo apt-get install unrar` or `sudo yum install unrar`
   - macOS: `brew install unrar`

## Usage

1. Run the application:
```bash
python main.py
```

2. Select your password-protected archive file
3. Select a text file containing candidate passwords (one per line)
4. Click "Start" to begin password testing
5. Monitor progress and results

## Security Notes

This tool is intended for legitimate purposes only:
- Testing your own forgotten passwords
- Security auditing with proper authorization
- Educational purposes

**Password Strength Recommendations:**
- Length matters more than complexity (NIST guidelines)
- Minimum 8 characters recommended
- Use unique passwords for different accounts
- Consider using a password manager

## File Formats

- **ZIP**: Supports standard ZIP encryption
- **RAR**: Supports RAR archive encryption (requires UnRAR)
- **Password Lists**: Plain text files with one password per line
