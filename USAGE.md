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
- **Enhance password list:** Generate password variations using common character substitutions (enabled by default)
- **Theme:** Use the View menu to switch between Light and Dark themes for comfortable viewing

### 3. Start Testing
- Click "Start Password Testing" to begin
- The progress bar will show current progress
- You can click "Stop" to cancel at any time

### 4. View Results
- **Success:** Shows "✔ Password found: [password]" in green
- **Failure:** Shows "❌ No password found" in red
- **Error:** Shows "⚠ Error: [message]" in orange

## Theme Support

The application supports both Light and Dark themes for comfortable viewing:

### Light Theme (Default)
- **Background:** Soft light gray (#F5F5F5) for reduced glare
- **Text:** Dark colors (#333333) for high contrast and readability
- **Accents:** Standard green, blue, and orange colors

### Dark Theme
- **Background:** Deep dark (#121212) for low-light environments
- **Surface:** Dark gray panels (#1E1E1E–#2A2A2A)
- **Text:** Light colors (#E0E0E0) optimized for dark backgrounds
- **Accents:** Vibrant colors (#50fa7b, #8be9fd, #ffb86c) for better visibility

### Switching Themes
1. Go to **View** menu in the menu bar
2. Select **Theme** submenu
3. Choose **Light Theme** or **Dark Theme**

The theme will switch immediately and all UI elements will update accordingly.

## Password Enhancement

The application includes an intelligent password enhancement feature that automatically generates variations of your password list using common character substitutions and patterns.

### How It Works

When **"Enhance password list"** is checked (default), the application will:

1. **Read your original password list**
2. **Generate variations** using common substitutions:
   - `a/A` → `@`, `4`
   - `e/E` → `3`
   - `i/I` → `1`, `!`
   - `o/O` → `0`
   - `s/S` → `$`, `5`
   - `t/T` → `7`
   - `l/L` → `1`
   - `g/G` → `9`
   - `b/B` → `6`

3. **Add common endings**: `123`, `!`, `1`, `12`, `2023`, `2024`, `01`
4. **Create capitalization variants**: First letter capitalized
5. **Remove duplicates** while preserving order

### Example Enhancement

Original password: `password`

Generated variations:
- `p@ssword` (a → @)
- `p4ssword` (a → 4)
- `passw0rd` (o → 0)
- `pa$$word` (s → $)
- `password123` (common ending)
- `Password` (capitalized)

### Benefits

- **Higher Success Rate**: Tests common password obfuscation patterns
- **Automatic**: No manual work required
- **Smart**: Avoids password explosion by limiting variations
- **Transparent**: Shows original vs enhanced count in the UI

### Password Testing Order

The application uses an intelligent testing order to maximize efficiency:

1. **Original passwords first** (positions 1-N)
2. **Enhanced variations second** (positions N+1 onwards)
3. **No duplicates** - variations matching originals are excluded

**Example:**
```
Original list: admin, test, hello
Testing order:
1. admin          ← Original
2. test           ← Original
3. hello          ← Original
4. @dmin          ← Enhanced
5. 4dmin          ← Enhanced
6. t3st           ← Enhanced
7. te$t           ← Enhanced
8. h3llo          ← Enhanced
9. hell0          ← Enhanced
... (more variations)
```

### Usage Tips

- **Enable by default** for better coverage
- **Disable** if you have a very large password list (>10,000 passwords)
- **Monitor** the enhanced count in the password list label
- **Original passwords** are always tested first for optimal efficiency

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
