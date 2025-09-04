# Privotron

Privotron is an open-source framework and automation tool designed to help individuals reclaim their privacy by opting out of data brokers. Data brokers collect, store, and sell personal information without explicit consent, posing significant privacy risks. Privotron makes the opt-out process easier by automating browser interactions with data broker websites.

## Why Privotron?

- **Privacy Protection**: Data brokers collect and sell your personal information without your explicit consent
- **Time Saving**: Manually opting out of dozens of data brokers can take hours or days
- **Automation**: Privotron automates the tedious process of filling out opt-out forms
- **Tracking**: Keep track of which brokers you've already opted out from
- **Community-Driven**: Easily contribute new broker configurations to help others

## Installation

### Prerequisites

- Python 3.13 or higher
- poetry (for dependency management)

### Installing Poetry

If you don't have Poetry installed, you can install it using one of these methods:

**Recommended (Official installer):**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Using pip:**
```bash
pip install poetry
```

**Using Homebrew (macOS):**
```bash
brew install poetry
```

**Using pipx (if you have it installed):**
```bash
pipx install poetry
```

After installation, you may need to restart your terminal or add Poetry to your PATH. Check that it's installed correctly:
```bash
poetry --version
```

### Using Poetry

```bash
# Clone the repository
git clone https://github.com/kevinl95/privotron.git
cd privotron

# Install dependencies
poetry install

# Install Playwright browsers
poetry run playwright install
```

**Option 1: Run commands directly with Poetry (Recommended)**
```bash
# Run the application directly
poetry run python main.py --help
poetry run python main.py --first "John" --last "Doe" --email "john@example.com" --zip "12345"
```

**Option 2: Activate the virtual environment**
```bash
# For Poetry 2.x, activate the virtual environment:
source $(poetry env info --path)/bin/activate

# For Poetry 1.x, use the shell:

poetry shell

# For Windows:
source $(poetry env info --path)/Scripts/activate

```

## Troubleshooting

### Playwright Browser Installation

If you see a message about installing browsers, run:
```bash
poetry run playwright install
```

## Getting Started

### Quick Start

```bash
# Run with your personal information
poetry run python main.py --first "John" --last "Doe" --email "john@example.com" --zip "12345"
```

### Creating a Profile

Save your information as a profile to avoid re-entering it:

```bash
poetry run python main.py --first "John" --last "Doe" --email "john@example.com" --phone "5551234567" --zip "12345" --save-profile "john"
```

### Using a Profile

```bash
# Use an existing profile
poetry run python main.py --profile "john"
```

### Parallel Processing

Process multiple brokers simultaneously to save time:

```bash
# Process up to 3 brokers at the same time
poetry run python main.py --profile "john" --parallel 3
```

## Skip Specific Brokers

You can skip specific brokers by adding their slugs to the `.skipbrokers` file in the brokers directory.

Example `.skipbrokers` file:
```
# Lines starting with # are comments
# Add one broker slug per line
acme
another_broker
```

The broker slug is defined in each broker's YAML file under the `slug` field.

## User Profiles

Privotron supports user profiles to save personal information and track which brokers have been processed for each user.

### Resetting Processed Brokers

```bash
# Reset the list of processed brokers for a profile
poetry run python main.py --profile "john" --reset
```

### Available Options

- `--first`: First name
- `--last`: Last name
- `--email`: Email address
- `--phone`: Phone number
- `--ssn`: Social Security Number
- `--city`: City
- `--state`: State (choose from US states)
- `--zip`: ZIP/Postal code
- `--profile`: Load saved profile
- `--save-profile`: Save current arguments as a profile
- `--reset`: Reset processed brokers for the profile
- `--parallel`: Number of brokers to process in parallel (default: 1)

## How It Works

- Profiles are stored in a `profiles` directory as JSON files
- Each profile tracks which brokers have been processed
- When using a profile, previously processed brokers are automatically skipped
- You can override saved information by providing command line arguments
- Parallel processing allows multiple opt-outs to run simultaneously
- State values are automatically converted between full names and abbreviations as needed
- First and last names can be automatically combined into full name formats

## Contributing

### Adding New Brokers

We welcome contributions of new broker configurations! For detailed information on adding new brokers, see [BROKER_GUIDE.md](BROKER_GUIDE.md).

### Development

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security Note

Social Security Numbers and other sensitive information are stored in profile files. 
These files are saved locally on your computer, but you should take appropriate 
precautions to protect this information:

- Ensure your computer is secured with a strong password
- Consider encrypting your disk
- Be careful when sharing your computer or profile files with others

## Broker Configuration Examples

### Full Name Handling

For forms that require a full name in a single field:

```yaml
# Standard format: "First Last"
- action: fill_full_name
  selector: "#fullName"
  
# Reversed format: "Last, First"
- action: fill_full_name
  selector: "#reversedName"
  format: reversed
```

### State Selection

For forms that require state selection, you can use the special `select_state` action:

```yaml
# For dropdowns that use state abbreviations (AL, AK, AZ, etc.)
- action: select_state
  selector: "#state"
  format: abbr
  
# For dropdowns that use full state names
- action: select_state
  selector: "#state"
```

### Select Options

There are multiple ways to select options from dropdowns:

```yaml
# Select by value attribute
- action: select
  selector: "#dropdown"
  value: "option1"
  
# Select by visible text/label
- action: select
  selector: "#dropdown"
  label: "Option 1"
  
# Select by index (0-based)
- action: select
  selector: "#dropdown"
  index: 0
  
# Select using a field from the user's data
- action: select
  selector: "#dropdown"
  field: city
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.