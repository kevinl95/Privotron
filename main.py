import click
import yaml
import time
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


@click.command(
    help="Automate opt-out process using browser automation",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option("--first", required=True)
@click.option("--last", required=True)
@click.option("--email", required=True)
@click.option("--zip", required=True)
def run_optout(first, last, email, zip):
    configs = []
    broker_dir = "brokers"
    skip_file = os.path.join(broker_dir, ".skipbrokers")
    skipped_brokers = []
    
    # Read skip file if it exists
    if os.path.exists(skip_file):
        try:
            with open(skip_file, "r") as f:
                skipped_brokers = [line.strip() for line in f if line.strip() and not line.startswith("#")]
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
                    # Skip this broker if its slug is in the skip list
                    if config.get("slug") in skipped_brokers:
                        print(f"Skipping {config['name']} (from skip file)")
                        continue
                    configs.append(config)
            except yaml.YAMLError as e:
                print(f"Error parsing {filename}: {e}")
                sys.exit(1)
            except FileNotFoundError:
                print(f"Could not find {filename}")
                sys.exit(1)
    data = {"first_name": first, "last_name": last, "email": email, "zip": zip}
    for config in configs:
        print(f"Processing {config['name']}...")
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


if __name__ == "__main__":
    run_optout()
