# Broker Configuration Guide

This guide explains how to add new data brokers to Privotron and documents all available action types for automating the opt-out process.

## Adding a New Broker

To add a new broker to Privotron, create a YAML file in the `brokers` directory with the following structure:

```yaml
name: Example Data Broker
slug: example_broker
url: https://www.exampledatabroker.com/optout
required_fields:
  - first_name
  - last_name
  - email
  - zip
steps:
  - action: navigate
    url: "https://www.exampledatabroker.com/optout"
  # Additional steps go here
```

### Required Fields

- `name`: Display name of the broker (shown in console output)
- `slug`: Unique identifier for the broker (used in skip files and profiles)
- `url`: Main URL of the broker's opt-out page
- `required_fields`: List of fields required by this broker (used for validation)
- `steps`: List of actions to perform for the opt-out process

## Available Actions

Privotron supports the following action types for automating the opt-out process:

### 1. Navigate

Navigate to a specific URL.

```yaml
- action: navigate
  url: "https://www.example.com/optout"
```

### 2. Fill

Fill a form field with user data.

```yaml
- action: fill
  selector: "#firstName"
  field: first_name
```

Available fields:
- `first_name`: User's first name
- `last_name`: User's last name
- `email`: User's email address
- `phone`: User's phone number
- `ssn`: User's social security number
- `zip`: User's ZIP/postal code
- `city`: User's city
- `state`: User's state (full name)
- `state_abbr`: User's state (two-letter abbreviation)

### 3. Fill Full Name

Fill a form field with the user's full name.

```yaml
# Standard format: "First Last"
- action: fill_full_name
  selector: "#fullName"
  
# Reversed format: "Last, First"
- action: fill_full_name
  selector: "#reversedName"
  format: reversed
```

### 4. Click

Click on an element.

```yaml
- action: click
  selector: "#submitButton"
```

### 5. Wait

Wait for a specified number of seconds.

```yaml
- action: wait
  seconds: 3
```

### 6. Select

Select an option from a dropdown menu.

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

### 7. Select State

Special action for selecting a state from a dropdown.

```yaml
# For dropdowns that use state abbreviations (AL, AK, AZ, etc.)
- action: select_state
  selector: "#state"
  format: abbr
  
# For dropdowns that use full state names
- action: select_state
  selector: "#state"
```

### 8. Prompt User to Select Record

Pause automation and prompt the user to manually select a record or perform an action.

```yaml
- action: prompt_user_to_select_record
  description: "Please select your record from the search results"
```

## Complete Example

Here's a complete example of a broker configuration:

```yaml
name: Acme Data Broker
slug: acme
url: https://www.acmedatabroker.com/optout
required_fields:
  - first_name
  - last_name
  - email
  - zip
steps:
  - action: navigate
    url: "https://www.acmedatabroker.com/optout"
  
  - action: fill
    selector: "#firstName"
    field: first_name
  
  - action: fill
    selector: "#lastName"
    field: last_name
  
  - action: fill
    selector: "#email"
    field: email
  
  - action: fill
    selector: "#zipCode"
    field: zip
  
  - action: select_state
    selector: "#state"
    format: abbr
  
  - action: click
    selector: "#searchButton"
  
  - action: wait
    seconds: 3
  
  - action: prompt_user_to_select_record
    description: "Please select your record from the search results"
  
  - action: click
    selector: "#confirmOptOut"
```

## Tips for Creating Broker Configurations

1. **Use Browser Developer Tools**: Use the browser's developer tools (F12) to inspect elements and find the correct selectors.

2. **Test Selectors**: Make sure your selectors are specific enough to target the right elements but not so specific that they break with minor page changes.

3. **Add Wait Steps**: Add wait steps after actions that trigger page loads or AJAX requests to ensure the page has time to update.

4. **Use Descriptive Names**: Give your broker a clear, descriptive name and a unique slug.

5. **Handle Manual Steps**: For steps that can't be automated (like CAPTCHA), use the `prompt_user_to_select_record` action to pause automation and allow manual intervention.

6. **Validate Required Fields**: List all required fields in the `required_fields` section to ensure the user provides all necessary information.

## Troubleshooting

If your broker configuration isn't working as expected:

1. **Check Selectors**: Verify that your selectors match the elements on the page.

2. **Add Wait Steps**: The page might need more time to load or process actions.

3. **Check for Dynamic Content**: Some pages load content dynamically, which might require additional wait steps or different selectors.

4. **Inspect Console Errors**: Look for errors in the console output that might indicate what's going wrong.

5. **Try Manual Steps**: If a particular step is failing, try using the `prompt_user_to_select_record` action to allow manual intervention for that step.