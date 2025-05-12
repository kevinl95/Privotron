import click
import yaml
import time
import os
import sys
import json
import asyncio
import concurrent.futures
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright


# State name to abbreviation mapping
STATE_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
}


@click.command(
    help="Automate opt-out process using browser automation",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option("--first", required=False, help="First name")
@click.option("--last", required=False, help="Last name")
@click.option("--email", required=False, help="Email address")
@click.option("--phone", required=False, help="Phone number")
@click.option("--ssn", required=False, help="Social Security Number")
@click.option("--city", required=False, help="City")
@click.option(
    "--state",
    required=False,
    help="State",
    type=click.Choice(
        [
            "Alabama",
            "Alaska",
            "Arizona",
            "Arkansas",
            "California",
            "Colorado",
            "Connecticut",
            "Delaware",
            "Florida",
            "Georgia",
            "Hawaii",
            "Idaho",
            "Illinois",
            "Indiana",
            "Iowa",
            "Kansas",
            "Kentucky",
            "Louisiana",
            "Maine",
            "Maryland",
            "Massachusetts",
            "Michigan",
            "Minnesota",
            "Mississippi",
            "Missouri",
            "Montana",
            "Nebraska",
            "Nevada",
            "New Hampshire",
            "New Jersey",
            "New Mexico",
            "New York",
            "North Carolina",
            "North Dakota",
            "Ohio",
            "Oklahoma",
            "Oregon",
            "Pennsylvania",
            "Rhode Island",
            "South Carolina",
            "South Dakota",
            "Tennessee",
            "Texas",
            "Utah",
            "Vermont",
            "Virginia",
            "Washington",
            "West Virginia",
            "Wisconsin",
            "Wyoming",
        ],
        case_sensitive=False
    ),
)
@click.option("--zip", required=False, help="ZIP/Postal code")
@click.option("--profile", required=False, help="Load saved profile")
@click.option(
    "--save-profile", required=False, help="Save current arguments as a profile"
)
@click.option("--reset", is_flag=True, help="Reset processed brokers for the profile")
@click.option(
    "--parallel", 
    default=1, 
    type=int, 
    help="Number of brokers to process in parallel (default: 1)"
)
def run_optout(first, last, email, phone, ssn, city, state, zip, profile, save_profile, reset, parallel):
    # Set up directories and files
    broker_dir = "brokers"
    skip_file = os.path.join(broker_dir, ".skipbrokers")
    profiles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")
    os.makedirs(profiles_dir, exist_ok=True)

    # Handle profile loading and saving
    user_data = {}
    processed_brokers = []
    profile_path = None

    if profile:
        profile_path = os.path.join(profiles_dir, f"{profile}.json")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r") as f:
                    user_data = json.load(f)

                # Load user info from profile if not provided in command line
                first = first or user_data.get("first_name")
                last = last or user_data.get("last_name")
                email = email or user_data.get("email")
                phone = phone or user_data.get("phone")
                ssn = ssn or user_data.get("ssn")
                city = city or user_data.get("city")
                state = state or user_data.get("state")
                zip = zip or user_data.get("zip")

                # Get list of already processed brokers
                if not reset:
                    processed_brokers = user_data.get("processed_brokers", [])
                    if processed_brokers:
                        print(
                            f"Previously processed brokers for {profile}: {', '.join(processed_brokers)}"
                        )

                print(f"Loaded profile: {profile}")
            except Exception as e:
                print(f"Error loading profile {profile}: {e}")
        else:
            print(
                f"Profile {profile} not found. Will create it if --save-profile is used."
            )

    # Check if we need to save this as a new profile
    if save_profile:
        if not all([first, last, email, zip]):
            print(
                "Error: All personal information (first, last, email, zip) must be provided to save a profile."
            )
            sys.exit(1)

        profile_path = os.path.join(profiles_dir, f"{save_profile}.json")
        user_data = {
            "first_name": first,
            "last_name": last,
            "email": email,
            "phone": phone,
            "ssn": ssn,
            "zip": zip,
            "city": city,
            "state": state,
            "processed_brokers": processed_brokers,
            "last_updated": datetime.now().isoformat(),
        }

        try:
            with open(profile_path, "w") as f:
                json.dump(user_data, f, indent=2)
            print(f"Saved profile: {save_profile}")
        except Exception as e:
            print(f"Error saving profile {save_profile}: {e}")

    # Validate required information
    if not all([first, last, email, zip]):
        print(
            "Error: Missing required information. Provide all options or use --profile."
        )
        sys.exit(1)

    configs = []
    skipped_brokers = []
    newly_processed_brokers = []

    # Read skip file if it exists
    if os.path.exists(skip_file):
        try:
            with open(skip_file, "r") as f:
                skipped_brokers = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
            print(f"Skipping brokers: {', '.join(skipped_brokers)}")
        except Exception as e:
            print(f"Warning: Could not read skip file: {e}")

    # Iterate through all yaml files in brokers directory
    for filename in os.listdir(broker_dir):
        if filename.endswith(".yaml"):
            yaml_path = os.path.join(broker_dir, filename)
            try:
                with open(yaml_path, "r") as f:
                    config = yaml.safe_load(f)
                    broker_slug = config.get("slug")

                    # Skip this broker if its slug is in the skip list
                    if broker_slug in skipped_brokers:
                        print(f"Skipping {config['name']} (from skip file)")
                        continue

                    # Skip if already processed for this profile
                    if broker_slug in processed_brokers:
                        print(f"Skipping {config['name']} (already processed)")
                        continue

                    configs.append(config)
                    newly_processed_brokers.append(broker_slug)
            except yaml.YAMLError as e:
                print(f"Error parsing {filename}: {e}")
                sys.exit(1)
            except FileNotFoundError:
                print(f"Could not find {filename}")
                sys.exit(1)

    # If no brokers to process, exit early
    if not configs:
        print("No brokers to process. All have been skipped or already processed.")
        return

    # Create data dictionary with both full state name and abbreviation
    data = {
        "first_name": first, 
        "last_name": last, 
        "email": email, 
        "phone": phone,
        "ssn": ssn,
        "zip": zip,
        "city": city,
        "state": state
    }
    
    # Add state abbreviation if state is provided
    if state and state in STATE_ABBR:
        data["state_abbr"] = STATE_ABBR[state]

    # Validate parallel value
    if parallel < 1:
        print("Parallel value must be at least 1. Setting to 1.")
        parallel = 1
    elif parallel > len(configs):
        print(f"Parallel value {parallel} is greater than number of brokers ({len(configs)}). Setting to {len(configs)}.")
        parallel = len(configs)

    # Choose processing method based on parallel value
    if parallel == 1:
        # Process brokers sequentially (original method)
        process_brokers_sequentially(configs, data, profile, profile_path)
    else:
        # Process brokers in parallel
        print(f"Processing {len(configs)} brokers with {parallel} parallel workers")
        process_brokers_in_parallel(configs, data, parallel)

    # Update profile with newly processed brokers
    if profile and profile_path and newly_processed_brokers:
        try:
            # Reload the profile in case it was modified elsewhere
            if os.path.exists(profile_path):
                with open(profile_path, "r") as f:
                    user_data = json.load(f)

            # Update the processed brokers list
            current_processed = user_data.get("processed_brokers", [])
            current_processed.extend(newly_processed_brokers)
            user_data["processed_brokers"] = list(
                set(current_processed)
            )  # Remove duplicates
            user_data["last_updated"] = datetime.now().isoformat()

            # Save the updated profile
            with open(profile_path, "w") as f:
                json.dump(user_data, f, indent=2)

            print(
                f"Updated profile {profile} with {len(newly_processed_brokers)} newly processed brokers"
            )
        except Exception as e:
            print(f"Error updating profile {profile}: {e}")


def process_brokers_sequentially(configs, data, profile, profile_path):
    """Process brokers one at a time (original method)"""
    for config in configs:
        print(f"Processing {config['name']}...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                for step in config["steps"]:
                    action = step["action"]
                    if action == "navigate":
                        page.goto(step["url"])
                    elif action == "fill":
                        page.fill(step["selector"], data[step["field"]])
                    elif action == "click":
                        page.click(step["selector"])
                    elif action == "wait":
                        time.sleep(step["seconds"])
                    elif action == "prompt_user_to_select_record":
                        print(step["description"])
                        print(
                            ">> Please select the correct record manually in the browser."
                        )
                        input("Press Enter once done...")
                    elif action == 'select':
                        if 'value' in step:
                            page.select_option(step['selector'], step['value'])
                        elif 'label' in step:
                            page.select_option(step['selector'], label=step['label'])
                        elif 'index' in step:
                            page.select_option(step['selector'], index=step['index'])
                        elif 'field' in step:
                            # Get the value from the data dictionary
                            field_value = data[step['field']]
                            page.select_option(step['selector'], field_value)
                    elif action == 'select_state':
                        # Special handling for state selection
                        if step.get('format') == 'abbr' and 'state_abbr' in data:
                            page.select_option(step['selector'], data['state_abbr'])
                        else:
                            page.select_option(step['selector'], data['state'])
                    else:
                        print(f"Unknown action: {action}")

                browser.close()
            print(f"✓ Completed {config['name']}")
        except Exception as e:
            print(f"✗ Error processing {config['name']}: {e}")


async def process_broker_async(config, data):
    """Process a single broker asynchronously"""
    print(f"Starting {config['name']}...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            for step in config["steps"]:
                action = step["action"]
                if action == "navigate":
                    await page.goto(step["url"])
                elif action == "fill":
                    await page.fill(step["selector"], data[step["field"]])
                elif action == "click":
                    await page.click(step["selector"])
                elif action == "wait":
                    await asyncio.sleep(step["seconds"])
                elif action == "prompt_user_to_select_record":
                    print(step["description"])
                    print(
                        f">> Please select the correct record manually in the browser for {config['name']}."
                    )
                    # This will block the current task but allow other tasks to continue
                    await asyncio.to_thread(input, f"Press Enter once done with {config['name']}...")
                elif action == 'select':
                    if 'value' in step:
                        await page.select_option(step['selector'], step['value'])
                    elif 'label' in step:
                        await page.select_option(step['selector'], label=step['label'])
                    elif 'index' in step:
                        await page.select_option(step['selector'], index=step['index'])
                    elif 'field' in step:
                        # Get the value from the data dictionary
                        field_value = data[step['field']]
                        await page.select_option(step['selector'], field_value)
                elif action == 'select_state':
                    # Special handling for state selection
                    if step.get('format') == 'abbr' and 'state_abbr' in data:
                        await page.select_option(step['selector'], data['state_abbr'])
                    else:
                        await page.select_option(step['selector'], data['state'])
                else:
                    print(f"Unknown action: {action}")

            await browser.close()
        print(f"✓ Completed {config['name']}")
        return True
    except Exception as e:
        print(f"✗ Error processing {config['name']}: {e}")
        return False


def process_broker_thread(config, data):
    """Process a single broker in a thread"""
    print(f"Starting {config['name']}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            for step in config["steps"]:
                action = step["action"]
                if action == "navigate":
                    page.goto(step["url"])
                elif action == "fill":
                    page.fill(step["selector"], data[step["field"]])
                elif action == "click":
                    page.click(step["selector"])
                elif action == "wait":
                    time.sleep(step["seconds"])
                elif action == "prompt_user_to_select_record":
                    print(step["description"])
                    print(
                        f">> Please select the correct record manually in the browser for {config['name']}."
                    )
                    input(f"Press Enter once done with {config['name']}...")
                elif action == 'select':
                    if 'value' in step:
                        page.select_option(step['selector'], step['value'])
                    elif 'label' in step:
                        page.select_option(step['selector'], label=step['label'])
                    elif 'index' in step:
                        page.select_option(step['selector'], index=step['index'])
                    elif 'field' in step:
                        # Get the value from the data dictionary
                        field_value = data[step['field']]
                        page.select_option(step['selector'], field_value)
                elif action == 'select_state':
                    # Special handling for state selection
                    if step.get('format') == 'abbr' and 'state_abbr' in data:
                        page.select_option(step['selector'], data['state_abbr'])
                    else:
                        page.select_option(step['selector'], data['state'])
                else:
                    print(f"Unknown action: {action}")

            browser.close()
        print(f"✓ Completed {config['name']}")
        return True
    except Exception as e:
        print(f"✗ Error processing {config['name']}: {e}")
        return False


def process_brokers_in_parallel(configs, data, parallel):
    """Process multiple brokers in parallel using thread pool"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        # Submit all tasks to the executor
        future_to_config = {
            executor.submit(process_broker_thread, config, data): config
            for config in configs
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_config):
            config = future_to_config[future]
            try:
                success = future.result()
                if not success:
                    print(f"Failed to process {config['name']}")
            except Exception as e:
                print(f"Exception processing {config['name']}: {e}")


if __name__ == "__main__":
    run_optout()