# Contributing to Green Bond Tracker

Thank you for your interest in contributing to the Green Bond Tracker project! This is an educational project aimed at helping people learn about green bonds, data analysis, and GIS visualization.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## 🤝 Code of Conduct

This project is dedicated to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Be respectful and professional
- Welcome newcomers and help them learn
- Accept constructive criticism gracefully
- Focus on what's best for the educational community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic knowledge of pandas, geopandas, and data visualization
- (Optional) Familiarity with GIS concepts

### Finding Issues to Work On

Good places to start:

1. **Good First Issues**: Look for issues labeled `good first issue`
2. **Documentation**: Help improve documentation (labeled `documentation`)
3. **Bug Fixes**: Fix bugs (labeled `bug`)
4. **Enhancements**: Add new features (labeled `enhancement`)

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/green-bond-tracker-project.git
cd green-bond-tracker-project

# Add upstream remote
git remote add upstream https://github.com/gabrielpriante/green-bond-tracker-project.git
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install project with development dependencies
pip install -e ".[dev]"

# OR install with all optional features (interactive maps, notebooks, dev tools)
pip install -e ".[all]"

# OR use the Makefile
make install

# Install pre-commit hooks
pre-commit install
```

### 4. Verify Installation

```bash
# Run tests to ensure everything is working
make test

# Run linter
make lint

# Try the CLI
gbt --version
gbt validate --input data/green_bonds.csv
```

### 5. Run Checks Locally (Before Pushing)

Run these commands to ensure your changes will pass CI:

```bash
# Using Makefile (recommended)
make lint        # Check code style
make format      # Auto-format code
make test        # Run tests with coverage

# Or manually
ruff check src/ tests/
ruff format src/ tests/
pytest tests/ -v --cov=src --cov-report=term-missing
```

## 🔧 How to Contribute

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Run linter
ruff check src/ tests/

# Run formatter
ruff format src/ tests/

# Check test coverage
pytest tests/ --cov=src --cov-report=html
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "feat: add interactive bubble map visualization"
# or
git commit -m "fix: correct validation of ISO country codes"
# or
git commit -m "docs: improve CLI usage examples"
```

**Commit Message Format**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request
```

## 📝 Coding Standards

### Python Style

- **PEP 8**: Follow Python's style guide
- **Line Length**: Maximum 100 characters
- **Type Hints**: Use type hints for function parameters and returns
- **Docstrings**: Use Google-style docstrings for all public functions

Example:

```python
def validate_country_code(code: str) -> bool:
    """
    Validate that a country code is a valid ISO 3166-1 alpha-3 code.

    Parameters
    ----------
    code : str
        The country code to validate

    Returns
    -------
    bool
        True if valid, False otherwise

    Examples
    --------
    >>> validate_country_code("USA")
    True
    >>> validate_country_code("US")
    False
    """
    return len(code) == 3 and code.isupper() and code.isalpha()
```

### Code Organization

- **Functions**: Keep functions small and focused (< 50 lines ideally)
- **Modules**: Group related functionality together
- **Imports**: Organize imports (standard library, third-party, local)
- **Constants**: Use UPPER_CASE for constants

### Educational Focus

- **Clarity over cleverness**: Code should be easy to understand for learners
- **Comments**: Explain *why*, not *what* (code should be self-documenting)
- **Examples**: Include examples in docstrings
- **Error messages**: Make error messages helpful and educational

## 🧪 Testing

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names: `test_validate_detects_negative_amounts`
- Follow the AAA pattern: Arrange, Act, Assert
- Use fixtures for common test data

Example:

```python
def test_validate_country_code_rejects_two_letter_codes():
    """Test that validation rejects 2-letter ISO codes."""
    # Arrange
    invalid_code = "US"

    # Act
    result = validate_country_code(invalid_code)

    # Assert
    assert result is False
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_validation.py

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run in watch mode (requires pytest-watch)
ptw tests/
```

### Test Coverage

- Aim for >80% code coverage
- Focus on testing business logic and validations
- Don't test external libraries (pandas, geopandas, etc.)

## 📚 Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings for all public functions/classes
2. **User Documentation**: README, usage guides, tutorials
3. **Developer Documentation**: This file, architecture docs
4. **Data Documentation**: Schema definitions, data dictionaries

### Documentation Style

- Use **Markdown** for all documentation files
- Include **code examples** wherever possible
- Use **clear headings** and table of contents for long docs
- Add **screenshots** for visual features

### Updating Documentation

When you change functionality:

1. Update relevant docstrings
2. Update README if user-facing changes
3. Update ROADMAP.md if affecting future plans
4. Add examples to docs/ if adding major features

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code passes all tests (`pytest tests/`)
- [ ] Code passes linting (`ruff check src/ tests/`)
- [ ] Code is formatted (`ruff format src/ tests/`)
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if applicable)
- [ ] Commits are clean and well-described

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
- [ ] Educational disclaimer maintained
```

### Review Process

1. Automated CI checks must pass
2. At least one maintainer review required
3. Address all review comments
4. Squash commits if requested
5. Maintainer will merge when approved

## 🎯 Areas for Contribution

### High Priority

- 📊 Additional visualizations (time series, treemaps, etc.)
- ✅ Enhanced validation rules
- 📖 Improved documentation and tutorials
- 🧪 More comprehensive test coverage
- 🌐 Interactive dashboard features

### Medium Priority

- 🔄 Data import from external sources
- 📧 Export to various formats (Excel, GeoJSON, etc.)
- 🎨 Customizable color schemes
- 📱 Responsive web interface

### Future Enhancements

- 🗺️ ArcGIS Online/Enterprise integration
- 🔍 Advanced filtering and querying
- 📈 Predictive analytics
- 🌍 Multi-language support

## 💡 Tips for Success

1. **Start Small**: Begin with documentation or small bug fixes
2. **Ask Questions**: Don't hesitate to ask in issues or discussions
3. **Be Patient**: Code review may take time
4. **Stay Focused**: One feature/fix per PR
5. **Learn Together**: This is an educational project - we're all learning!

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Request Comments**: For code review questions

## 🙏 Recognition

All contributors will be recognized in:

- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Green Bond Tracker! Your efforts help make this educational resource better for everyone. 🌱

---

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## ⚠️ Educational Disclaimer

Remember: This project is for educational purposes only and should not be used for investment advice or financial decision-making.
