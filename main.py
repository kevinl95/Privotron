import click
import yaml
import time
from playwright.sync_api import sync_playwright

@click.command()
@click.option('--first', required=True)
@click.option('--last', required=True)
@click.option('--email', required=True)
@click.option('--zip', required=True)
def run_optout(first, last, email, zip):
    with open('acme_plugin.yaml', 'r') as f:
        config = yaml.safe_load(f)

    data = {
        'first_name': first,
        'last_name': last,
        'email': email,
        'zip': zip
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for step in config['steps']:
            action = step['action']
            if action == 'navigate':
                page.goto(step['url'])
            elif action == 'fill':
                page.fill(step['selector'], data[step['field']])
            elif action == 'click':
                page.click(step['selector'])
            elif action == 'wait':
                time.sleep(step['seconds'])
            elif action == 'prompt_user_to_select_record':
                print(step['description'])
                print(">> Please select the correct record manually in the browser.")
                input("Press Enter once done...")
            else:
                print(f"Unknown action: {action}")

        browser.close()

if __name__ == '__main__':
    run_optout()