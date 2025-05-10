import click
import yaml
import time
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright


@click.command(
    help="Automate opt-out process using browser automation",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option("--first", required=False, help="First name")
@click.option("--last", required=False, help="Last name")
@click.option("--email", required=False, help="Email address")
@click.option("--zip", required=False, help="ZIP/Postal code")
@click.option("--profile", required=False, help="Load saved profile")
@click.option(
    "--save-profile", required=False, help="Save current arguments as a profile"
)
@click.option("--reset", is_flag=True, help="Reset processed brokers for the profile")
def run_optout(first, last, email, zip, profile, save_profile, reset):
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
            "zip": zip,
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

    data = {"first_name": first, "last_name": last, "email": email, "zip": zip}

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
                    else:
                        print(f"Unknown action: {action}")

                browser.close()

            # Mark this broker as processed
            if profile and profile_path:
                processed_brokers.append(config.get("slug"))
        except Exception as e:
            print(f"Error processing {config['name']}: {e}")

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


if __name__ == "__main__":
    run_optout()
