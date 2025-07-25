# Zirar Usage Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **For RAR support (optional):**
   - **Windows:**
     - Download UnRAR from https://www.rarlab.com/rar_add.htm
     - Or run: `python setup_unrar.py` for guided setup
   - **Linux:** `sudo apt-get install unrar`
   - **macOS:** `brew install unrar`

## Running the Application

```bash
python main.py
```

## How to Use

### 1. Select Files
- **Archive File:** Click "Browse..." next to "Archive File" and select your password-protected ZIP or RAR file
- **Password List:** Click "Browse..." next to "Password List" and select a text file containing candidate passwords (one per line)

### 2. Configure Options
- **Show current attempt:** Check this box if you want to see the actual passwords being tested (otherwise they're masked with asterisks)

### 3. Start Testing
- Click "Start Password Testing" to begin
- The progress bar will show current progress
- You can click "Stop" to cancel at any time

### 4. View Results
- **Success:** Shows "✔ Password found: [password]" in green
- **Failure:** Shows "❌ No password found" in red  
- **Error:** Shows "⚠ Error: [message]" in orange

## Password List Format

Create a text file with one password per line:
```
password123
admin
letmein
qwerty
secret
```

## Security Notes

### Ethical Use Only
This tool should only be used for:
- Testing your own forgotten passwords
- Authorized security auditing
- Educational purposes

### Password Strength Tips (NIST Guidelines)
- **Length matters more than complexity**
- Minimum 8 characters recommended
- Use unique passwords for different accounts
- Consider using a password manager

## Supported Formats

- **ZIP Files:** Standard ZIP encryption and AES encryption (if pyzipper is installed)
- **RAR Files:** RAR archive encryption (requires UnRAR executable)

## Troubleshooting

### "RAR Support Error"
- **Windows:** Run `python setup_unrar.py` for guided setup
- **Linux:** `sudo apt-get install unrar`
- **macOS:** `brew install unrar`
- Ensure UnRAR is in your system PATH
- Restart the application after installing UnRAR

### "Could not read password file"
- Check file permissions
- Ensure file is in UTF-8 encoding
- Verify file contains at least one password

### "Permission Error"
- Check that you have read access to both files
- Try running as administrator (Windows) or with sudo (Linux/macOS) if needed

### Application Won't Start
- Verify Python 3.8+ is installed
- Install all requirements: `pip install -r requirements.txt`
- Check for any missing dependencies

## Performance Tips

- **Large password lists:** The application will show progress, but very large lists (millions of passwords) may take considerable time
- **Complex archives:** Some archive formats may be slower to test than others
- **System resources:** The application uses minimal CPU and memory, but disk I/O may be a factor for large archives

## Testing the Application

Use the provided test files:

1. **Create test archives:**
   ```bash
   python create_test_archives.py
   ```

2. **Test with sample data:**
   - Select `test_archive_test123.zip`
   - Select `sample_passwords.txt`
   - Start testing (should find password "test123")

## Legal and Ethical Considerations

- Only use on files you own or have explicit permission to test
- Respect applicable laws and regulations
- Consider the ethical implications of password cracking
- This tool is for legitimate security testing and recovery purposes only
