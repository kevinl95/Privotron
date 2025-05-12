# Privotron

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

### Creating a Profile

```bash
# Create a new profile while running the opt-out process
python main.py --first "John" --last "Doe" --email "john@example.com" --phone "555-123-4567" --ssn "123-45-6789" --zip "12345" --save-profile "john"
```

### Using a Profile

```bash
# Use an existing profile (no need to provide personal info again)
python main.py --profile "john"
```

### Parallel Processing

Privotron can process multiple brokers simultaneously to save time:

```bash
# Process up to 3 brokers at the same time
python main.py --profile "john" --parallel 3
```

### Resetting Processed Brokers

```bash
# Reset the list of processed brokers for a profile
python main.py --profile "john" --reset
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

### How It Works

- Profiles are stored in a `profiles` directory as JSON files
- Each profile tracks which brokers have been processed
- When using a profile, previously processed brokers are automatically skipped
- You can override saved information by providing command line arguments
- Parallel processing allows multiple opt-outs to run simultaneously
- State values are automatically converted between full names and abbreviations as needed
- First and last names can be automatically combined into full name formats

For detailed information on adding new brokers, see [BROKER_GUIDE.md](BROKER_GUIDE.md).

### Security Note

Social Security Numbers and other sensitive information are stored in profile files. 
These files are saved locally on your computer, but you should take appropriate 
precautions to protect this information:

- Ensure your computer is secured with a strong password
- Consider encrypting your disk
- Be careful when sharing your computer or profile files with others

## Broker Configuration

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