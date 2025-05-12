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

### Security Note

Social Security Numbers and other sensitive information are stored in profile files. 
These files are saved locally on your computer, but you should take appropriate 
precautions to protect this information:

- Ensure your computer is secured with a strong password
- Consider encrypting your disk
- Be careful when sharing your computer or profile files with others