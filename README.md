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
python main.py --first "John" --last "Doe" --email "john@example.com" --zip "12345" --save-profile "john"
```

### Using a Profile

```bash
# Use an existing profile (no need to provide personal info again)
python main.py --profile "john"
```

### Resetting Processed Brokers

```bash
# Reset the list of processed brokers for a profile
python main.py --profile "john" --reset
```

### How It Works

- Profiles are stored in a `profiles` directory as JSON files
- Each profile tracks which brokers have been processed
- When using a profile, previously processed brokers are automatically skipped
- You can override saved information by providing command line arguments