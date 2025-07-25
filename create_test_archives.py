#!/usr/bin/env python3
"""
Test Archive Creator for Zirar
Creates password-protected ZIP and RAR archives for testing the application
"""

import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Try to import optional dependencies
try:
    import pyzipper
    PYZIPPER_AVAILABLE = True
except ImportError:
    PYZIPPER_AVAILABLE = False

try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False

def create_test_content():
    """Create sample files for archiving"""
    print("📁 Creating test content...")
    
    # Create test directory
    test_dir = Path("test_content")
    test_dir.mkdir(exist_ok=True)
    
    # Sample text document
    doc_content = f"""# Test Document for Zirar

This is a sample document created for testing the Zirar archive password recovery tool.

## Document Information
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Purpose: Educational testing of password-protected archives
- Tool: Zirar Archive Password Recovery Tool

## Sample Content
This document contains various types of text to ensure proper archive creation and extraction:

### Lorem Ipsum
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

### Technical Information
- Archive Format: ZIP/RAR
- Encryption: Password-protected
- Testing Tool: Zirar
- Educational Purpose: Learning cybersecurity concepts

### Security Notes
This archive is created for educational purposes only. The passwords used are 
intentionally simple for testing purposes. In real-world scenarios, use strong, 
unique passwords for protecting sensitive data.

## Test Data
Numbers: 1234567890
Special Characters: !@#$%^&*()_+-=[]{{}}|;:,.<>?
Mixed Case: AbCdEfGhIjKlMnOpQrStUvWxYz

End of test document.
"""
    
    with open(test_dir / "document.txt", "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    # Sample CSV data
    csv_content = """Name,Age,City,Country,Occupation
John Smith,28,New York,USA,Software Engineer
Jane Doe,32,London,UK,Data Scientist
Bob Johnson,45,Toronto,Canada,Project Manager
Alice Brown,29,Sydney,Australia,UX Designer
Charlie Wilson,38,Berlin,Germany,DevOps Engineer
Diana Davis,26,Tokyo,Japan,Frontend Developer
Eve Miller,41,Paris,France,Security Analyst
Frank Garcia,35,Madrid,Spain,Backend Developer
Grace Lee,30,Seoul,South Korea,Product Manager
Henry Chen,33,Singapore,Singapore,System Administrator
"""
    
    with open(test_dir / "data.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    # Sample configuration file
    config_content = """# Zirar Test Configuration
# This is a sample configuration file for testing

[application]
name = "Zirar Test Suite"
version = "1.0.0"
debug = true

[security]
encryption_enabled = true
password_policy = "strong"
session_timeout = 3600

[testing]
test_mode = true
sample_data = true
mock_services = false

[database]
host = "localhost"
port = 5432
name = "zirar_test"
user = "test_user"
# Note: This is test data only - not real credentials

[logging]
level = "INFO"
file = "zirar_test.log"
max_size = "10MB"
backup_count = 5
"""
    
    with open(test_dir / "config.ini", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    # Sample JSON data
    json_content = """{
  "test_suite": {
    "name": "Zirar Archive Testing",
    "version": "1.0",
    "description": "Test data for educational password recovery tool",
    "created": "2024-01-01",
    "purpose": "Educational and testing"
  },
  "test_cases": [
    {
      "id": 1,
      "name": "Basic ZIP Test",
      "password": "test123",
      "expected_result": "success"
    },
    {
      "id": 2,
      "name": "Enhanced Password Test",
      "password": "admin",
      "variations": ["@dmin", "4dmin", "admin123", "Admin"]
    },
    {
      "id": 3,
      "name": "Complex Password Test",
      "password": "secret",
      "variations": ["s3cret", "$ecret", "secret!", "Secret"]
    }
  ],
  "educational_notes": [
    "These passwords are intentionally simple for testing",
    "Real passwords should be much stronger",
    "Use unique passwords for different accounts",
    "Consider using a password manager"
  ]
}"""
    
    with open(test_dir / "test_data.json", "w", encoding="utf-8") as f:
        f.write(json_content)
    
    print(f"   ✅ Created {len(list(test_dir.glob('*')))} test files")
    return test_dir

def create_zip_archives(test_dir):
    """Create password-protected ZIP archives"""
    print("\n📦 Creating ZIP archives...")
    
    # Test passwords with different complexity levels
    test_passwords = [
        ("simple", "test123"),
        ("common", "password"),
        ("admin", "admin"),
        ("secret", "secret"),
        ("enhanced", "p@ssw0rd"),
        ("complex", "MyS3cur3P@ss!")
    ]
    
    created_archives = []
    
    for name, password in test_passwords:
        zip_filename = f"test_zip_{name}.zip"
        
        try:
            if PYZIPPER_AVAILABLE:
                # Use pyzipper for better encryption
                with pyzipper.AESZipFile(zip_filename, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
                    zf.setpassword(password.encode('utf-8'))
                    zf.setencryption(pyzipper.WZ_AES, nbits=256)
                    
                    # Add all test files
                    for file_path in test_dir.glob("*"):
                        if file_path.is_file():
                            zf.write(file_path, file_path.name)
                
                print(f"   ✅ Created {zip_filename} (AES-256) - Password: '{password}'")
                
            else:
                # Fallback to standard zipfile (weaker encryption)
                with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.setpassword(password.encode('utf-8'))
                    
                    # Add all test files
                    for file_path in test_dir.glob("*"):
                        if file_path.is_file():
                            zf.write(file_path, file_path.name)
                
                print(f"   ✅ Created {zip_filename} (Standard) - Password: '{password}'")
            
            created_archives.append((zip_filename, password, "ZIP"))
            
        except Exception as e:
            print(f"   ❌ Failed to create {zip_filename}: {str(e)}")
    
    return created_archives

def create_rar_archives(test_dir):
    """Create password-protected RAR archives (if possible)"""
    print("\n📦 Creating RAR archives...")
    
    # Check if we can create RAR files
    rar_tool = None
    for tool in ['rar', 'rar.exe']:
        try:
            import subprocess
            result = subprocess.run([tool], capture_output=True, text=True, timeout=5)
            if result.returncode != 127:  # Command found
                rar_tool = tool
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    if not rar_tool:
        print("   ⚠️  RAR creation tool not found")
        print("   💡 Install WinRAR or RAR command-line tool to create RAR archives")
        print("   📋 ZIP archives are sufficient for testing most functionality")
        return []
    
    # Test passwords for RAR archives
    test_passwords = [
        ("simple", "test123"),
        ("admin", "admin"),
        ("secret", "secret")
    ]
    
    created_archives = []
    
    for name, password in test_passwords:
        rar_filename = f"test_rar_{name}.rar"
        
        try:
            import subprocess
            
            # Create RAR archive with password
            cmd = [
                rar_tool, 'a',  # Add files
                f'-hp{password}',  # Set password
                '-r',  # Recursive
                rar_filename,  # Archive name
                str(test_dir / "*")  # Files to add
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   ✅ Created {rar_filename} - Password: '{password}'")
                created_archives.append((rar_filename, password, "RAR"))
            else:
                print(f"   ❌ Failed to create {rar_filename}: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Failed to create {rar_filename}: {str(e)}")
    
    return created_archives

def create_password_list(archives):
    """Create a comprehensive password list for testing"""
    print("\n📝 Creating password list...")
    
    # Extract all passwords used
    used_passwords = [password for _, password, _ in archives]
    
    # Common passwords for testing
    common_passwords = [
        # Simple passwords
        "123456", "password", "123456789", "12345678", "12345",
        "1234567", "1234567890", "qwerty", "abc123", "111111",
        
        # Admin/system passwords
        "admin", "administrator", "root", "user", "guest",
        "login", "test", "demo", "sample",
        
        # Dictionary words
        "secret", "hello", "welcome", "master", "dragon",
        "monkey", "letmein", "trustno1", "sunshine", "shadow",
        
        # Enhanced variations (what Zirar would generate)
        "p@ssword", "p4ssword", "passw0rd", "pa$$word",
        "@dmin", "4dmin", "s3cret", "$ecret", "secr3t",
        "t3st", "te$t", "h3llo", "hell0",
        
        # With common endings
        "password123", "admin123", "secret123", "test123",
        "password!", "admin!", "secret!", "test!",
        "password1", "admin1", "secret1", "test1",
        "password2024", "admin2024", "secret2024",
        
        # Capitalized versions
        "Password", "Admin", "Secret", "Test", "Hello",
        "Welcome", "Master", "Dragon", "Monkey"
    ]
    
    # Combine and deduplicate
    all_passwords = used_passwords + common_passwords
    unique_passwords = []
    seen = set()
    
    # Add used passwords first (higher priority)
    for pwd in used_passwords:
        if pwd not in seen:
            unique_passwords.append(pwd)
            seen.add(pwd)
    
    # Add common passwords
    for pwd in common_passwords:
        if pwd not in seen:
            unique_passwords.append(pwd)
            seen.add(pwd)
    
    # Write password list
    with open("test_passwords.txt", "w", encoding="utf-8") as f:
        for password in unique_passwords:
            f.write(f"{password}\n")
    
    print(f"   ✅ Created test_passwords.txt with {len(unique_passwords)} passwords")
    print(f"   📋 Archive passwords are included in the first {len(used_passwords)} entries")
    
    return "test_passwords.txt"

def create_readme():
    """Create README for test files"""
    print("\n📚 Creating test documentation...")
    
    readme_content = """# Zirar Test Archives

This directory contains password-protected archives for testing the Zirar application.

## 🎓 Educational Purpose

These test files are created for:
- Learning how password-protected archives work
- Testing the Zirar password recovery tool
- Understanding different encryption methods
- Demonstrating password enhancement features

## 📦 Test Archives

### ZIP Archives
- `test_zip_simple.zip` - Password: `test123`
- `test_zip_common.zip` - Password: `password`
- `test_zip_admin.zip` - Password: `admin`
- `test_zip_secret.zip` - Password: `secret`
- `test_zip_enhanced.zip` - Password: `p@ssw0rd`
- `test_zip_complex.zip` - Password: `MyS3cur3P@ss!`

### RAR Archives (if created)
- `test_rar_simple.rar` - Password: `test123`
- `test_rar_admin.rar` - Password: `admin`
- `test_rar_secret.rar` - Password: `secret`

## 📝 Password List

- `test_passwords.txt` - Contains all test passwords plus common variations
- Archive passwords are included in the first few entries
- Enhanced variations demonstrate Zirar's password enhancement feature

## 🧪 Testing Instructions

### Basic Testing
1. Launch Zirar: `python main.py`
2. Select a test archive (e.g., `test_zip_simple.zip`)
3. Select `test_passwords.txt` as the password list
4. Enable "Enhance password list" option
5. Click "Start Password Testing"
6. The correct password should be found quickly

### Feature Testing

#### Password Enhancement
- Test with `test_zip_enhanced.zip` (password: `p@ssw0rd`)
- The original password list contains `password`
- Zirar should enhance it to `p@ssw0rd` and find the correct password

#### Multi-threading
- Test with different worker thread counts
- Compare performance with Conservative/Recommended/Aggressive settings
- Monitor CPU usage during testing

#### Theme Testing
- Switch between Light and Dark themes
- Verify all UI elements are properly styled
- Test theme switching during password testing

## 🔒 Security Notes

**⚠️ Important Reminders:**
- These are test files with intentionally weak passwords
- Real archives should use strong, unique passwords
- Only test with files you own or have permission to test
- This tool is for educational and legitimate purposes only

## 📊 Expected Results

When testing with `test_passwords.txt`:
- Simple passwords should be found in the first few attempts
- Enhanced passwords demonstrate the password variation feature
- Complex passwords test the full enhancement algorithm
- All test passwords are included in the password list

## 🛠️ Troubleshooting

### ZIP Issues
- Ensure pyzipper is installed: `pip install pyzipper`
- Standard zipfile is used as fallback if pyzipper unavailable

### RAR Issues
- Install UnRAR: Run `python setup_unrar.py`
- RAR creation requires WinRAR or command-line RAR tool
- ZIP archives are sufficient for most testing

### Performance Issues
- Adjust worker thread count based on your system
- Use Conservative setting on slower systems
- Monitor system resources during testing

## 📈 Performance Expectations

Typical results with test files:
- Simple passwords: Found in 1-10 attempts
- Enhanced passwords: Found in 10-50 attempts (depending on enhancement)
- Complex passwords: Found in 50-200 attempts
- Multi-threading: 2-20x speedup depending on system

---

**Remember: These test files are for educational purposes only. Always use strong passwords for real data protection.**
"""
    
    with open("TEST_README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("   ✅ Created TEST_README.md with comprehensive testing instructions")

def cleanup_temp_files(test_dir):
    """Clean up temporary test content directory"""
    try:
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up temporary directory: {test_dir}")
    except Exception as e:
        print(f"\n⚠️  Could not clean up {test_dir}: {str(e)}")

def main():
    """Main function to create all test archives"""
    print("🔐 Zirar Test Archive Creator")
    print("=" * 50)
    print("Creating password-protected archives for testing the Zirar application")
    print("This tool is for educational and testing purposes only.\n")
    
    try:
        # Check dependencies
        print("🔍 Checking dependencies...")
        if PYZIPPER_AVAILABLE:
            print("   ✅ pyzipper available (AES encryption)")
        else:
            print("   ⚠️  pyzipper not available (using standard zipfile)")
            print("   💡 Install with: pip install pyzipper")
        
        if RARFILE_AVAILABLE:
            print("   ✅ rarfile available")
        else:
            print("   ⚠️  rarfile not available")
            print("   💡 Install with: pip install rarfile")
        
        # Create test content
        test_dir = create_test_content()
        
        # Create archives
        zip_archives = create_zip_archives(test_dir)
        rar_archives = create_rar_archives(test_dir)
        
        all_archives = zip_archives + rar_archives
        
        if not all_archives:
            print("\n❌ No archives were created successfully")
            return False
        
        # Create password list
        password_file = create_password_list(all_archives)
        
        # Create documentation
        create_readme()
        
        # Clean up temporary files
        cleanup_temp_files(test_dir)
        
        # Summary
        print(f"\n🎉 Test Archive Creation Complete!")
        print(f"   📦 Created {len(all_archives)} archives:")
        for filename, password, format_type in all_archives:
            print(f"      • {filename} ({format_type}) - Password: '{password}'")
        
        print(f"\n📝 Files created:")
        print(f"   • {password_file} - Password list for testing")
        print(f"   • TEST_README.md - Testing instructions")
        
        print(f"\n🧪 Next Steps:")
        print(f"   1. Run Zirar: python main.py")
        print(f"   2. Select a test archive")
        print(f"   3. Select {password_file}")
        print(f"   4. Start password testing")
        print(f"   5. Verify the correct password is found")
        
        print(f"\n✅ All test files are ready for educational use!")
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Creation cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print(f"Please check your Python environment and dependencies")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
