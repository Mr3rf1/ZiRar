# Contributing to Zirar

Thank you for your interest in contributing to Zirar! This project is dedicated to educational purposes and ethical security research. We welcome contributions that enhance the educational value and maintain the ethical standards of this project.

## 🎓 Educational Mission

This project exists to:
- Teach cybersecurity concepts and password security
- Demonstrate responsible security research practices
- Provide hands-on learning opportunities
- Promote ethical hacking and responsible disclosure

## 🤝 How to Contribute

### Types of Contributions We Welcome

1. **Educational Enhancements**
   - Improved documentation and tutorials
   - Code comments and explanations
   - Educational examples and demonstrations
   - Security best practices documentation

2. **Technical Improvements**
   - Bug fixes and stability improvements
   - Performance optimizations
   - User interface enhancements
   - Cross-platform compatibility

3. **Security Features**
   - Enhanced error handling
   - Better input validation
   - Security-focused improvements
   - Ethical use enforcement

4. **Testing and Quality Assurance**
   - Unit tests and integration tests
   - Performance benchmarks
   - Documentation testing
   - Cross-platform testing

### What We Don't Accept

- Features that could facilitate unauthorized access
- Contributions that bypass security measures
- Code that could be used for malicious purposes
- Anything that contradicts our educational mission

## 📋 Contribution Process

### 1. Before You Start

- Read our [Code of Conduct](#code-of-conduct)
- Review the [Educational Use License](LICENSE)
- Check existing issues and pull requests
- Discuss major changes in an issue first

### 2. Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/Mr3rf1/zirar.git
cd zirar

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

### 3. Making Changes

```bash
# Create a feature branch
git checkout -b feature/educational-enhancement

# Make your changes
# ... edit files ...

# Test your changes
python -m pytest
python main.py  # Manual testing

# Format code
black .
flake8 .

# Commit changes
git add .
git commit -m "Add educational feature: description"

# Push to your fork
git push origin feature/educational-enhancement
```

### 4. Submitting a Pull Request

1. **Create a Pull Request** from your fork to the main repository
2. **Provide a clear description** of your changes
3. **Explain the educational value** of your contribution
4. **Include tests** if applicable
5. **Update documentation** as needed

## 📝 Code Standards

### Code Quality
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Include docstrings for all functions and classes
- Add type hints where appropriate
- Keep functions focused and concise

### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Include usage examples
- Document security considerations

### Testing
- Write tests for new functionality
- Ensure existing tests pass
- Test on multiple platforms if possible
- Include edge case testing

## 🛡️ Security Guidelines

### Responsible Development
- Never include actual passwords or sensitive data
- Use placeholder data in examples
- Implement proper error handling
- Validate all user inputs

### Ethical Considerations
- Ensure features support legitimate use cases
- Include appropriate warnings and disclaimers
- Document potential security implications
- Promote responsible use practices

## 🎯 Code of Conduct

### Our Standards

**Positive Behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on educational value
- Promoting ethical security practices

**Unacceptable Behavior:**
- Harassment or discriminatory language
- Promoting illegal or unethical activities
- Sharing malicious code or techniques
- Violating the educational mission
- Disrespecting community guidelines

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## 🏷️ Issue Guidelines

### Bug Reports
- Use a clear and descriptive title
- Describe the expected vs actual behavior
- Include steps to reproduce
- Provide system information
- Include relevant logs or screenshots

### Feature Requests
- Explain the educational value
- Describe the proposed functionality
- Consider alternative solutions
- Discuss potential security implications

### Security Issues
- Report security vulnerabilities privately
- Use responsible disclosure practices
- Allow time for fixes before public disclosure
- Follow coordinated vulnerability disclosure

## 📚 Resources

### Educational Materials
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Security Guidelines](https://owasp.org/)
- [Ethical Hacking Resources](https://www.eccouncil.org/ethical-hacking/)

### Development Resources
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Git Best Practices](https://git-scm.com/book)

## 🙏 Recognition

Contributors who make significant educational contributions will be:
- Listed in the project acknowledgments
- Credited in release notes
- Invited to join the maintainer team (for ongoing contributors)

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Issues**: Create a GitHub Issue
- **Security**: Contact maintainers privately
- **General**: Check existing documentation first

Thank you for helping make Zirar a valuable educational resource while maintaining the highest ethical standards!

---

**Remember: Every contribution should enhance the educational value while promoting ethical and responsible use of security tools.**
