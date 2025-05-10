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