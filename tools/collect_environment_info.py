
import argparse
import json
import re
from playwright.sync_api import sync_playwright

def get_environment_info(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until='networkidle')
            content = page.content()
            
            # 1. Extract CMS Version from HTML comment
            cms_version = "N/A"
            match = re.search(r'<!-- Page Info: CMS-Version: (.*?) -->', content)
            if match:
                cms_version = match.group(1).strip()

            # 2. Get Browser Version
            browser_version = browser.version

            # 3. Feature-App-Versionen (Placeholder - needs specific logic for the target app)
            # This is highly dependent on the application. 
            # For this example, we'll assume it might be in a global JS variable or a meta tag.
            # As a placeholder, we'll just add a static value.
            feature_app_versions = {
                "app-shell": "1.2.3", # Example value
                "configuration-service": "2.1.0" # Example value
            }

            env_info = {
                "url": url,
                "cms_version": cms_version,
                "browser": {
                    "name": "Chrome",
                    "version": browser_version
                },
                "feature_app_versions": feature_app_versions,
            }
            
            return env_info

        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Collect environment information from a web page.')
    parser.add_argument('--url', type=str, required=True, help='The URL to collect information from.')
    parser.add_argument('--output-file', type=str, required=True, help='The path to the output JSON file.')
    
    args = parser.parse_args()
    
    environment_data = get_environment_info(args.url)
    
    with open(args.output_file, 'w') as f:
        json.dump(environment_data, f, indent=4)
        
    print(f"Environment information successfully saved to {args.output_file}")
