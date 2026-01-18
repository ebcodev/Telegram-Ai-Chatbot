# Contributing to Telegram Bot Using OpenAI

Thank you for your interest in contributing to this project! We welcome contributions from the community to help improve the bot's functionality, fix bugs, and add new features. Please follow these guidelines to ensure a smooth collaboration process.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md) (if available; otherwise, treat others with respect and kindness).

## How to Contribute

### Reporting Bugs

- Check if the issue already exists in the [Issues](https://github.com/eblancode/telegram-ai-chatbot/issues) section.
- If not, create a new issue with a clear title and description.
- Include steps to reproduce, expected vs. actual behavior, screenshots (if applicable), and your environment (Python version, OS, etc.).

### Suggesting Enhancements

- Open an issue describing the feature you'd like to add.
- Explain why it would be useful and how it fits with the project's goals (e.g., new OpenAI models, better audio handling, or UI improvements in Telegram).

### Setting Up for Development

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```
   git clone https://github.com/your-username/telegram-ai-chatbot.git
   cd telegram-ai-chatbot
   ```
3. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `config.ini` file as described in the [README](./README.md).
6. Run the bot locally:
   ```
   python src/main.py
   ```

### Code Style Guidelines

- Follow PEP 8 for Python code.
- Use meaningful variable/function names.
- Add docstrings for functions and classes.
- Ensure code is readable and well-commented where necessary.
- Run linting tools if possible (e.g., `flake8` or `black` for formatting).

### Submitting Pull Requests

1. Create a new branch for your changes:
   ```
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit them with descriptive messages.
3. Test your changes thoroughly (e.g., run the bot and verify features).
4. Push to your fork:
   ```
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request (PR) on the original repository.
   - Provide a clear title and description.
   - Reference any related issues (e.g., "Fixes #123").
   - Be patient; maintainers will review as soon as possible.

### First-Time Contributors

If you're new to open-source, look for issues labeled "good first issue" or "help wanted." We're here to help!

## Questions?

Feel free to open an issue for discussions or reach out via the project's communication channels.

Thanks for contributing! 🚀
